import logging
from neurons.apify.actors import run_actor, ActorConfig

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)


class RedditScraperLite:
    """
    A class designed to scrap reddit posts based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the RedditScraperLite.
        """
        self.actor_config = ActorConfig("oAuCIx3ItNrs2okjQ")

    def searchByUrl(
        self, urls: list = ["https://twitter.com/elonmusk/status/1384874438472844800"]
    ):
        """
        Search for reddit posts given a set of urls.
        """
        run_input = {
            "debugMode": False,
            "maxComments": 1,
            "maxCommunitiesCount": 1,
            "maxItems": 1,
            "maxPostCount": 1,
            "maxUserCount": 1,
            "proxy": {"useApifyProxy": True},
            "scrollTimeout": 40,
            "searchComments": False,
            "searchCommunities": False,
            "searchPosts": True,
            "searchUsers": False,
            "searches": ["t3_104vus0"],
            "skipComments": False,
            "startUrls": [{"url": urls[0]}],
        }
        return self.map(run_actor(self.actor_config, run_input))

    def execute(
        self,
        search_queries: list = ["bittensor"],
        limit_number: int = 15,
        validator_key: str = "None",
        validator_version: str = None,
        miner_uid: int = 0,
    ) -> list:
        """
        Execute the reddit post query process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of reddit posts.
        """
        run_input = {
            "debugMode": False,
            "maxComments": 10,
            "maxCommunitiesCount": 2,
            "maxItems": 10,
            "maxPostCount": 10,
            "maxUserCount": 2,
            "proxy": {"useApifyProxy": True},
            "scrollTimeout": 40,
            "searchComments": False,
            "searchCommunities": False,
            "searchPosts": True,
            "searchUsers": False,
            "searches": search_queries,
            "skipComments": False,
        }

        return self.map(run_actor(self.actor_config, run_input))

    def map(self, input: list) -> list:
        """
        Potentially map the input data as needed. As of now, this method serves as a placeholder and simply returns the
        input data directly.

        Args:
            input (list): The data to potentially map or transform.

        Returns:
            list: The mapped or transformed data.
        """
        filtered_input = [
            {
                "id": item["id"],
                "url": item["url"],
                "text": item["body"],
                "likes": item["upVotes"],
                "dataType": item["dataType"],
                "community": item["communityName"],
                "username": item["username"],
                "parent": item.get("parentId"),
                "timestamp": item["createdAt"],
            }
            for item in input
        ]
        return filtered_input


if __name__ == "__main__":
    # Initialize the RedditScraperLite query mechanism with the actor configuration
    query = RedditScraperLite()

    # Execute the search for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the data
    for item in data_set:
        print(item)
