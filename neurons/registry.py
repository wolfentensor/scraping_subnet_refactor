import asyncio
import logging
from logging import getLogger
from typing import *
from neurons.structures.priority_queue import AsyncPriorityQueue
from neurons.abstract.plugin import ScrapingPlugin
from queries import QueryType
from bittensor.axon import axon as Axon
from bittensor.synapse import Synapse
from bittensor import __version__
from packaging import version
from packaging.specifiers import SpecifierSet

logger = getLogger(__name__)


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[QueryType, Dict[str, Any]] = {}
        self._loop = asyncio.get_running_loop()

    def register_plugin(self, target: QueryType, plugin: ScrapingPlugin):
        logger.log(logging.INFO, f"Registering plugin {plugin}")

        self._plugins[target] = {
            'forward_fn': plugin.forward_fn,
            'blacklist_fn': plugin.blacklist_fn,
            'priority_fn': plugin.priority_fn,
            'verify_fn': plugin.verify_fn
        }
        try:
            Axon.attach(**self._plugins[target])
            self._plugins[target]['inputs'] = AsyncPriorityQueue()
            self._plugins[target]['outputs'] = AsyncPriorityQueue()
        except Exception as exc:
            logger.log(logging.ERROR, f"Could not attach {target} plugin {plugin} to Axon", exc_info=exc)
            del self._plugins[target]

    def _version_check(self, plugin: ScrapingPlugin):
        specifier_set = SpecifierSet(plugin.REQUIRED_VERSION)
        if version.parse(__version__) in specifier_set:
            print("The plugin version is compatible.")
        else:
            print("The plugin version is not compatible.")
            exit(1)

    def get_target_plugin(self, target: QueryType) -> Dict[str, Any]:
        return self._plugins.get(target, None)

    def get_target_input_q(self, target: QueryType) -> AsyncPriorityQueue:
        return self._plugins.get(target, {}).get('inputs')

    def get_target_output_q(self, target: QueryType) -> AsyncPriorityQueue:
        return self._plugins.get(target, {}).get('outputs')

    async def acall_target_forward_fn(self, synapse: Synapse, target: QueryType, data: Any) -> Any:
        return await self._plugins[target]['blacklist_fn'](synapse, data)

    async def acall_target_blacklist_fn(self, synapse: Synapse, target: QueryType, data: Any) -> bool:
        return await self._plugins[target]['blacklist_fn'](synapse, data)

    async def acall_target_priority_fn(self, synapse: Synapse, target: QueryType, data: Any) -> int:
        return await self._plugins[target]['priority_fn'](synapse, data)

    async def acall_target_verify_fn(self, synapse: Synapse, target: QueryType, data: Any) -> bool:
        return await self._plugins[target]['verify_fn'](synapse, data)

    async def call_target_forward_fn(self, synapse: Synapse, target: QueryType, data: Any) -> Any:
        return self._plugins[target]['blacklist_fn'](synapse, data)

    async def call_target_blacklist_fn(self, synapse: Synapse, target: QueryType, data: Any) -> bool:
        return self._plugins[target]['blacklist_fn'](synapse, data)

    async def call_target_priority_fn(self, synapse: Synapse, target: QueryType, data: Any) -> int:
        return self._plugins[target]['priority_fn'](synapse, data)

    async def call_target_verify_fn(self, synapse: Synapse, target: QueryType, data: Any) -> bool:
        return self._plugins[target]['verify_fn'](synapse, data)
