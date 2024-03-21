import asyncio
from abc import ABC, abstractmethod
import bittensor as bt
from typing import *
from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Type
from neurons.structures.source import Version
import asyncio
from neurons.structures.priority_queue import AsyncPriorityQueue
from neurons.abstract.source import ScrapingSource


class PluginManager:
    def __init__(self):
        self._plugins: Dict[ScrapingSource, Dict[str, Any]] = {}

    async def register_plugin(self, source: ScrapingSource):
        self._plugins[source] = {
            'inputs': AsyncPriorityQueue(),
            'outputs': AsyncPriorityQueue()
        }

        self._plugins[source]['forward_fn'] = source.forward_fn
        self._plugins[source]['blacklist_fn'] = source.blacklist_fn
        self._plugins[source]['priority_fn'] = source.priority_fn
        self._plugins[source]['verify_fn'] = source.verify_fn

    async def get_plugin_queues(self, source: ScrapingSource) -> Dict[str, Any]:
        return self._plugins.get(source, None)

    def call_forward_fn(self, source: ScrapingSource, data: Any) -> Any:
        return self._plugins[source]['forward_fn'](data)

    def call_blacklist_fn(self, source: ScrapingSource, data: Any) -> bool:
        return self._plugins[source]['blacklist_fn'](data)

    def call_priority_fn(self, source: ScrapingSource, data: Any) -> int:
        return self._plugins[source]['priority_fn'](data)

    def call_verify_fn(self, source: ScrapingSource, data: Any) -> bool:
        return self._plugins[source]['verify_fn'](data)

