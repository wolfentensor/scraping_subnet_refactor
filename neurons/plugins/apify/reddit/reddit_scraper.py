import logging
from neurons.apify.actors import run_actor, ActorConfig
from typing import Optional

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)


class RedditScraper:
    """
    A class designed to scrap reddit posts based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the RedditScraper
        """
        self.actor_config = ActorConfig("FgJtjDwJCLhRH9saM")

    def searchByUrl(
        self, urls: Optional[list] = None
    ):
        """
        Search for reddit posts by url.
        """
        urls = ["https://twitter.com/elonmusk/status/1384874438472844800"] if urls is None else urls
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
            "skipComments": False,
            "startUrls": [{"url": urls[0]}],
        }
        return self.map(run_actor(self.actor_config, run_input))

    def execute(
        self, search_queries: Optional[list] = None, limit_number: int = 15
    ) -> list:
        """
        Execute the reddit post query process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of reddit posts.
        """
        search_queries = ["bittensor"] if search_queries is None else search_queries
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
                "timestamp": item["createdAt"],
            }
            for item in input
        ]
        return filtered_input


if __name__ == "__main__":
    # Initialize the reddit scraper query mechanism
    query = RedditScraper()

    # Execute the query for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the returned data
    for item in data_set:
        print(item)
