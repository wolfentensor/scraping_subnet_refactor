import asyncio
from typing import *
import logging

from injector import Module, provider, singleton, Injector
from pika import ConnectionParameters
from pika.adapters.asyncio_connection import AsyncioConnection

from infrastruture.banshee.abstract import AbstractTransport

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class RabbitMQTransport(AbstractTransport):
    def __init__(self, connection_parameters: ConnectionParameters):
        self.connection_parameters = connection_parameters
        self.loop = asyncio.get_event_loop()
        self.connection: Optional[AsyncioConnection] = None

    async def connect(self):
        """Create an asynchronous RabbitMQ connection."""
        self.connection = AsyncioConnection(self.connection_parameters,
                                            on_open_callback=self.on_connection_open,
                                            on_open_error_callback=self.on_connection_open_error,
                                            on_close_callback=self.on_connection_closed,
                                            custom_ioloop=self.loop)

        # Wait for connection to open
        await self.connection.connected

    def on_connection_open(self, _unused_connection):
        print("Connection opened")

    def on_connection_open_error(self, _unused_connection, err):
        print(f"Connection open failed: {err}")

    def on_connection_closed(self, _unused_connection, reason):
        print(f"Connection closed: {reason}")

    async def send(self, data: bytes, queue_name: str) -> None:
        if not self.connection or self.connection.is_closed:
            await self.connect()

        channel = self.connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=data)

    async def setup_listener(self, queue_name: str, callback) -> None:
        if not self.connection or self.connection.is_closed:
            await self.connect()

        channel = self.connection.channel()

        def on_message(ch, method, properties, body):
            asyncio.create_task(callback(body))

        channel.basic_consume(queue=queue_name,
                              on_message_callback=on_message,
                              auto_ack=True)
        print(f"Listening on {queue_name}...")


class RmqTransportModule(Module):
    @singleton
    @provider
    def provide_transport(self) -> AbstractTransport:
        connection_parameters = ConnectionParameters(host='localhost')
        return RabbitMQTransport(connection_parameters)


# Example implementation

async def process_message(body):
    print(f"Received message: {body}")


async def main():
    injector = Injector([RmqTransportModule])
    transport: AbstractTransport = injector.get(AbstractTransport)

    await transport.connect()
    await transport.setup_listener("test_queue", process_message)
    await transport.send(b"Hello, RabbitMQ!", "test_queue")

if __name__ == "__main__":
    asyncio.run(main())