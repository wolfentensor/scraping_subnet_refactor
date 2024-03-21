import orjson as json
from injector import inject, Injector, Module, provider, singleton
from infrastruture.banshee.abstract import TransportProtocol


class TransportModule(Module):
    @singleton
    @provider
    def provide_transport_medium(self) -> TransportProtocol:
        # Example implementation that should be replaced with a real transport medium like RabbitMQ or Redis
        class InMemoryTransportMedium(TransportProtocol):
            def __init__(self):
                self.messages = {}

            async def send(self, channel: str, message: str) -> None:
                self.messages[channel] = message

            async def receive(self, channel: str) -> str:
                return self.messages.get(channel, "")

        return InMemoryTransportMedium()



