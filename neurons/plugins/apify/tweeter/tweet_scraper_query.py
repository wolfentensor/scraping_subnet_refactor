from neurons.apify.actors import run_actor, ActorConfig
from typing import Optional


class TweetScraperQuery:
    """
    A class designed to scrape tweets based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the TweetScraperQuery.
        """
        self.actor_config = ActorConfig("2s3kSMq7tpuC3bI6M")

    def execute(
        self, search_queries: Optional[list] = None, limit_number: int = 15
    ) -> list:
        """
        Execute the tweet scraping process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of scraped tweet data.
        """
        search_queries = ["bittensor"] if search_queries is None else search_queries
        run_input = {
            "excludeImages": False,
            "excludeLinks": False,
            "excludeMedia": False,
            "excludeNativeRetweets": False,
            "excludeNativeVideo": False,
            "excludeNews": False,
            "excludeProVideo": False,
            "excludeQuote": False,
            "excludeReplies": False,
            "excludeSafe": False,
            "excludeVerified": False,
            "excludeVideos": False,
            "images": False,
            "includeUserId": True,
            "includeUserInfo": True,
            "language": "any",
            "links": False,
            "media": False,
            "nativeRetweets": False,
            "nativeVideo": False,
            "news": False,
            "proVideo": False,
            "proxyConfig": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
            "quote": False,
            "replies": False,
            "safe": False,
            "searchQueries": search_queries,
            "tweetsDesired": 10,
            "verified": False,
            "videos": False,
        }
        return self.map(run_actor(self.actor_config, run_input))

    def map(self, input_data: list) -> list:
        """
        Potentially map the input data as needed. As of now, this method serves as a placeholder and simply returns the
        input data directly.

        Args:
            input_data (list): The data to potentially map or transform.

        Returns:
            list: The mapped or transformed data.
        """
        filtered_input = [
            {
                "id": item["tweet_id"],
                "url": item["url"],
                "text": item["text"],
                "likes": item["likes"],
                "images": item["images"],
                "timestamp": item["timestamp"],
            }
            for item in input_data
        ]
        return filtered_input


if __name__ == "__main__":
    # Initialize the tweet scraper query mechanism
    query = TweetScraperQuery(actor_config=_config)

    # Execute the scraper for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the scraped data
    for item in data_set:
        print(item)
