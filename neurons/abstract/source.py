import asyncio
from abc import ABC, abstractmethod
import bittensor as bt
from typing import *
from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Type
from neurons.structures.source import Version
import asyncio


class ScrapingSource(ABC, bt.Synapse):
    """
    Extends the Bittensor Synapse with an additional version attribute,
    used for compatibility and version control in operations.
    """
    version: Optional[Version] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._source_config = None
        self._source_metagraph = None
        self._source_synapse = None

    @abstractmethod
    async def configure(self, synapse, metagraph, synapse_config):
        pass

    @abstractmethod
    async def forward_fn(self, query):
        raise NotImplemented("Concrete subclasses must implement forward_fn")

    @abstractmethod
    async def blacklist_fn(self, query):
        raise NotImplemented("Concrete subclasses must implemented blacklist_fn")

    @abstractmethod
    async def priority_fn(self, query):
        raise NotImplemented("Concrete subclasses must implement priority_fn")

    @abstractmethod
    async def verify_fn(self, query):
        raise NotImplemented("Concrete subclasses must implement verify_fn")

    @abstractmethod
    async def deserialize(self) -> "bt.Synapse":
        raise NotImplemented("Concrete subclasses must implement deserialize")







