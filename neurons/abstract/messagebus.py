from abc import ABC, abstractmethod
from typing import Any
from typing import *


class AbstractMessageBus(ABC):
    @abstractmethod
    def publish(self, topic: str, message: str) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        pass
