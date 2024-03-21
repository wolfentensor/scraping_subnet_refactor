from typing import *
from abc import ABC, abstractmethod


class AbstractTransport(ABC):

    @abstractmethod
    async def send(self, data: bytes, queue_name: str) -> None:
        """Send data to a specified queue."""
        pass

    @abstractmethod
    async def setup_listener(self, queue_name: str, callback) -> None:
        """Listen for messages from a specified queue and process them using a callback."""
        pass

