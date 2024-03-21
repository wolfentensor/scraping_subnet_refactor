from abc import ABC, abstractmethod
from typing import Optional
import bittensor as bt
from packaging.version import Version


class ScrapingPlugin(ABC, bt.Synapse):
    """
    Abstract base class for Bittensor scraping_subnet plugins.
    These plugins operate on behalf of miners to produce results,
    adding functionalities like configuration, request processing, and
    response validation. Incorporates a version attribute for compatibility
    and version control among different plugin implementations.

    Attributes:
        version (Optional[Version]): Specifies the plugin version for compatibility checks.
    """

    version: Optional[Version] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._source_config = None
        self._source_metagraph = None
        self._source_synapse = None

    @abstractmethod
    async def configure(self, synapse, metagraph, synapse_config):
        """Configures the plugin with necessary parameters."""
        pass

    @abstractmethod
    async def forward_fn(self, query):
        """
        Defines the forward function for processing queries.

        Args:
            query: The query to process.

        Raises:
            NotImplemented: If the subclass has not implemented this method.
        """
        raise NotImplemented("Concrete subclasses must implement forward_fn")

    @abstractmethod
    async def blacklist_fn(self, query):
        """
        Defines the blacklist function to filter out queries.

        Args:
            query: The query to evaluate.

        Raises:
            NotImplemented: If the subclass has not implemented this method.
        """
        raise NotImplemented("Concrete subclasses must implemented blacklist_fn")

    @abstractmethod
    async def priority_fn(self, query):
        """
        Assigns priority to queries for processing.

        Args:
            query: The query to prioritize.

        Raises:
            NotImplemented: If the subclass has not implemented this method.
        """
        raise NotImplemented("Concrete subclasses must implement priority_fn")

    @abstractmethod
    async def verify_fn(self, query):
        """
        Verifies the integrity or validity of the query response.

        Args:
            query: The query response to verify.

        Raises:
            NotImplemented: If the subclass has not implemented this method.
        """
        raise NotImplemented("Concrete subclasses must implement verify_fn")

    @abstractmethod
    async def deserialize(self) -> "bt.Synapse":
        """
        Deserializes the plugin configuration to a bittensor.Synapse object.

        Raises:
            NotImplemented: If the subclass has not implemented this method.
        """
        raise NotImplemented("Concrete subclasses must implement deserialize")
