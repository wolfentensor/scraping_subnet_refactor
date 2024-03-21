from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable
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
        plugin_name (Optional[str]): Specifies the plugin name.
        plugin_author (Optional[str]): Specifies the plugin author.
        plugin_version (Optional[str]): Specifies the plugin version for compatibility checks.
        bittensor_version (Optional[Version]): Specifies the bittensor version for compatibility checks.
        version (Optional[Version]): an alias of bittensor_version for backwards compatibility.
    """
    REQUIRED_VERSION = ">=6.9.3"

    plugin_name: Optional[str] = None
    plugin_target: Optional[str] = None
    plugin_author: Optional[str] = None
    plugin_version: Optional[str] = None
    version = REQUIRED_VERSION

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._source_config = None
        self._source_metagraph = None
        self._source_synapse = None

    def __str__(self):
        return f"{self.plugin_name} {self.plugin_version} (Bittensor {self.bittensor_version})"

    def __repr__(self):
        return (f"{self.__class__.__name__}(plugin_name={self.plugin_name!r}, "
                f"plugin_author={self.plugin_author!r}, plugin_version={self.plugin_version!r}, "
                f"bittensor_version={self.bittensor_version!r})")

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
    async def blacklist_fn(self, query) -> Tuple[bool, str]:
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


