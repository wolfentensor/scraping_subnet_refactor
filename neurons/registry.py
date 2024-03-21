from typing import Any, Callable, Dict, Type
from neurons.structures.priority_queue import AsyncPriorityQueue
from neurons.abstract.plugin import ScrapingPlugin
from queries import QueryType


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[QueryType, Dict[str, Any]] = {}

    async def register_plugin(self, target: QueryType, plugin: ScrapingPlugin):
        self._plugins[target] = {
            'inputs': AsyncPriorityQueue(),
            'outputs': AsyncPriorityQueue(),
            'forward_fn': plugin.forward_fn,
            'blacklist_fn': plugin.blacklist_fn,
            'priority_fn': plugin.priority_fn,
            'verify_fn': plugin.verify_fn
        }

    async def get_plugin_queues(self, target: QueryType) -> Dict[str, Any]:
        return self._plugins.get(target, None)

    def call_forward_fn(self, target: QueryType, data: Any) -> Any:
        return self._plugins[target]['forward_fn'](data)

    def call_blacklist_fn(self, target: QueryType, data: Any) -> bool:
        return self._plugins[target]['blacklist_fn'](data)

    def call_priority_fn(self, target: QueryType, data: Any) -> int:
        return self._plugins[target]['priority_fn'](data)

    def call_verify_fn(self, target: QueryType, data: Any) -> bool:
        return self._plugins[target]['verify_fn'](data)

