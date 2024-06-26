import asyncio
from neurons.abstract import ScrapingSource
from neurons.structures.priority_queue import AsyncPriorityQueue
from typing import *


class RedditSource(ScrapingSource):
    """
    RedditScrap class inherits from ScrapingSource class.
    It is used to scrape data from Reddit.
    """

    def __init__(self, scrap_input, scrap_output, *args, **kwargs):

        # Required request input, filled by sending dendrite caller.
        super().__init__(*args, **kwargs)
        scrap_input: Optional[Dict] = None

        # Optional request output, filled by receiving axon.
        # TODO: Add error handling for when scrap_output is None
        scrap_output: Optional[List[Dict]] = None

    async def deserialize(self) -> List[Dict]:
        """
        Deserialize the scrap_output into a list of dictionaries.
        """
        # TODO: Add error handling for when scrap_output is None
        return self.scrap_output


    async def configure(self, synapse, metagraph, synapse_config):
        pass

    async def fetch_data(self, query):
        pass


    async def blacklist_reddit(self, synapse: scraping.protocol.RedditScrap) -> Tuple[bool, str]:
        """
        This function runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.
        Below: Check that the hotkey is a registered entity in the metagraph.
        """
        if synapse.dendrite.hotkey not in metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, ""
        # are not validators, or do not have enough stake. This can be checked via metagraph.S
        # and metagraph.validator_permit. You can always attain the uid of the sender via a
        # metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.
        # Otherwise, allow the request to be processed further.
        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, ""



    # The priority function determines the order in which requests are handled.
    # More valuable or higher-priority requests are processed before others.
    async def priority_reddit(self, synapse: scraping.protocol.RedditScrap) -> float:
        """
        Miners may recieve messages from multiple entities at once. This function
        determines which request should be processed first. Higher values indicate
        that the request should be processed first. Lower values indicate that the
        request should be processed later.
        Below: simple logic, prioritize requests from entities with more stake.
        """
        caller_uid = metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(metagraph.S[caller_uid])  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority

    async def fetch_data(
            self,
        synapse: scraping.protocol.RedditScrap,
    ) -> scraping.protocol.RedditScrap:
        """
        This function runs after the RedditScrap synapse has been deserialized (i.e. after synapse.data is available).
        This function runs after the blacklist and priority functions have been called.
        """
        validator_uid = metagraph.hotkeys.index(synapse.dendrite.hotkey)

        # Version checking
        validator_version_str = None
        if synapse.version is None:
            bt.logging.info(
                f"Received redditScrap request from validator without version (validator uid = {validator_uid})"
            )
        elif not scraping.utils.check_version(synapse.version):
            synapse.version = scraping.utils.get_my_version()
            return synapse
        else:
            validator_version_str = f"{synapse.version.major_version}.{synapse.version.minor_version}.{synapse.version.patch_version}"

        # If update is scheduled, not accept any request
        if scraping.utils.update_flag:
            return synapse

        bt.logging.info(
            f"Search from validator(version={validator_version_str}): {synapse.scrap_input} \n"
        )
        if synapse.scrap_input is not None and len(synapse.scrap_input) > 0:
            search_key = synapse.scrap_input["search_key"]
        else:
            search_key = [random_line()]
            bt.logging.info(f"picking random keyword: {search_key} \n")
        # Fetch latest N posts from miner's local database.
        posts = reddit_query.execute(
            search_key,
            15,
            synapse.dendrite.hotkey,
            validator_version_str,
            my_subnet_uid,
        )
        synapse.scrap_output = posts
        synapse.version = scraping.utils.get_my_version()
        bt.logging.info(
            f"✅ success: returning {len(synapse.scrap_output)} reddit posts\n"
        )
        return synapse
