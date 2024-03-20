import asyncio
from abc import ABC, abstractmethod
import bittensor as bt
from typing import *
from pydantic import BaseModel


class Version(BaseModel):
    """
    Represents a software version with major, minor, and patch components.
    """
    major_version: Optional[int] = None
    minor_version: Optional[int] = None
    patch_version: Optional[int] = None


class ScrapingSource(ABC, bt.Synapse):
    """
    Extends the Bittensor Synapse with an additional version attribute,
    used for compatibility and version control in operations.
    """

    version: Optional[Version] = None

    @abstractmethod
    async def fetch_data(self, query):
        pass

    @abstractmethod
    async def configure(self, synapse, metagraph, synapse_config):
        pass




