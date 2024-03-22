"""
This is the main module for the miner. It includes the necessary imports, the configuration setup, and the main function that runs the miner.

The MIT License (MIT)
Copyright © 2023 Chris Wilson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# Importing necessary libraries and modules
import os
import sys
import time
import asyncio
import argparse
import traceback
import bittensor as bt
import scraping
from typing import Tuple
import random
import torch
from neurons.queries import get_query, QueryType, QueryProvider
from neurons.plugins.twitter import TwitterSource
from neurons.plugins.reddit import RedditSource
from neurons.structures.priority_queue import AsyncPriorityQueue

# TODO: Check if all the necessary libraries are installed and up-to-date


async def get_config():
    """
    This function initializes the necessary command-line arguments.
    Using command-line arguments allows users to customize various miner settings.
    """
    parser = argparse.ArgumentParser()
    # Adds override arguments for network and netuid.
    parser.add_argument("--netuid", type=int, default=3, help="The chain subnet uid.")
    parser.add_argument(
        "--auto-update",
        type=str,
        default=True,
        help='Set to "no" to disable auto update.',
    )
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)
    # Adds axon specific arguments i.e. --axon.port ...
    bt.axon.add_args(parser)
    # Activating the parser to read any command-line inputs.
    # To print help message, run python3 neurons/miner.py --help
    config = bt.config(parser)

    # Set up logging directory
    # Logging captures events for diagnosis or understanding miner's behavior.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            "miner",
        )
    )
    # Ensure the directory for logging exists, else create one.
    if not os.path.exists(config.full_path):
        os.makedirs(config.full_path, exist_ok=True)
    return config


# TODO: Add error handling for when the directory for logging cannot be created




async def random_line(a_file="keywords.txt"):
    if not os.path.exists(a_file):
        print(f"Keyword file not found at location: {a_file}")
        quit()
    lines = open(a_file).read().splitlines()
    return random.choice(lines)


# Main takes the config and starts the miner.
class Miner:

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


    def __init__(self, config):
        """
        This function takes the configuration and starts the miner.
        It sets up the necessary Bittensor objects, attaches the necessary functions to the axon, and starts the main loop.
        """
        self.config = config
        
    async def execute(self):
        twitter_query = get_query(QueryType.TWITTER, QueryProvider.TWEET_FLASH)
        reddit_query = get_query(QueryType.REDDIT, QueryProvider.REDDIT_SCRAPER_LITE)
        # Activating Bittensor's logging with the set configurations.
        bt.logging(config=self.config, logging_dir=self.config.full_path)
        bt.logging.info(
            f"Running miner for subnet: {self.config.netuid} on network: {self.config.subtensor.chain_endpoint} with config:"
        )

        # This logs the active configuration to the specified logging directory for review.
        bt.logging.info(self.config)

        # Initialize Bittensor miner objects
        # These classes are vital to interact and function within the Bittensor network.
        bt.logging.info("Setting up bittensor objects.")
        # Wallet holds cryptographic information, ensuring secure transactions and communication.
        wallet = bt.wallet(config=self.config)
        bt.logging.info(f"Wallet: {wallet}")

        # subtensor manages the blockchain connection, facilitating interaction with the Bittensor blockchain.
        subtensor = bt.subtensor(config=self.config)
        bt.logging.info(f"Subtensor: {subtensor}")

        # metagraph provides the network's current state, holding state about other participants in a subnet.
        metagraph = bt.metagraph(
            network=subtensor.network, netuid=self.config.netuid, sync=False
        )
        try:
            metagraph.load()
            bt.logging.info(f"Updated metagraph from cache.")
        except Exception as e:
            metagraph = subtensor.metagraph(self.config.netuid)

        if subtensor.block - metagraph.block.item() > 5:
            metagraph = subtensor.metagraph(self.config.netuid)
            bt.logging.info(f"Saved metagraph is old, syncing with subtensor")

        bt.logging.info(f"Metagraph: {metagraph}")

        last_updated_block = subtensor.block - 100

        if wallet.hotkey.ss58_address not in metagraph.hotkeys:
            bt.logging.error(
                f"\nYour miner: {wallet} is not registered to chain connection: {subtensor} \nRun btcli wallet register and try again. "
            )
            exit()
        else:
            # Each miner gets a unique identity (UID) in the network for differentiation.
            my_subnet_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
            bt.logging.info(f"Running miner on uid: {my_subnet_uid}")

    def build(self):
        # Build and link miner functions to the axon.
        # The axon handles request processing, allowing validators to send this process requests.

        axon = bt.axon(wallet=wallet, port=self.config.axon.port)
        bt.logging.info(f"Axon {axon}")

        # Attach determiners which functions are called when servicing a request.
        bt.logging.info(f"Attaching forward function to axon.")
        axon.attach(forward_fn=redditScrap).attach(
            forward_fn=twitterScrap,
            # blacklist_fn = blacklist_twitter,
            # priority_fn = priority_twitter,
        )

        # Serve passes the axon information to the network + netuid we are hosting on.
        # This will auto-update if the axon port of external ip have changed.
        bt.logging.info(
            f"Serving axon {redditScrap, twitterScrap} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
        )
        axon.serve(netuid=self.config.netuid, subtensor=subtensor)

        # Start  starts the miner's axon, making it active on the network.
        bt.logging.info(f"Starting axon server on port: {self.config.axon.port}")
        axon.start()

        # Keep the miner alive
        # This loop maintains the miner's operations until intentionally stopped.
        bt.logging.info(f"Starting main loop")
        step = 0
        while True:
            try:
                # Below: Periodically update our knowledge of the network graph.
                if step % 60 == 0:
                    try:
                        metagraph.load()
                        bt.logging.info(f"Updated metagraph from cache.")
                    except Exception as e:
                        metagraph = subtensor.metagraph(self.config.netuid)

                    if subtensor.block - metagraph.block.item() > 5:
                        bt.logging.info(f"Metagraph is old, syncing with subtensor")
                        metagraph = subtensor.metagraph(self.config.netuid)

                    log = (
                        f"Step:{step} | "
                        f"Block:{metagraph.block.item()} | "
                        f"Stake:{metagraph.S[my_subnet_uid]} | "
                        f"Rank:{metagraph.R[my_subnet_uid]} | "
                        f"Trust:{metagraph.T[my_subnet_uid]} | "
                        f"Consensus:{metagraph.C[my_subnet_uid] } | "
                        f"Incentive:{metagraph.I[my_subnet_uid]} | "
                        f"Emission:{metagraph.E[my_subnet_uid]}"
                    )
                    bt.logging.info(log)

                    # Check for auto update
                    if self.config.auto_update != "no":
                        if scraping.utils.update_repository(self.config.auto_update):
                            bt.logging.success("🔁 Repository updated, exiting miner")
                            exit(0)

                step += 1
                time.sleep(1)

            # If someone intentionally stops the miner, it'll safely terminate operations.
            except KeyboardInterrupt:
                axon.stop()
                bt.logging.success("Miner killed by keyboard interrupt.")
                break
            # In case of unforeseen errors, the miner will log the error and continue operations.
            except Exception as e:
                bt.logging.error(traceback.format_exc())
                continue


async def main(config):
    async with Miner(config) as miner:
        await miner.execute()

# This is the main function, which runs the miner.
if __name__ == "__main__":
    asyncio.run(main(get_config()))

