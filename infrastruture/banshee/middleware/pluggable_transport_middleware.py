import logging
from typing import *

import orjson as json
from injector import inject, Injector, Module, provider, singleton
import banshee
import banshee.context
import banshee.message
import banshee.request
import banshee.errors

from infrastruture.banshee.abstract import AbstractTransport

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GenericTransportMiddleware(banshee.message.Middleware):
    @inject
    def __init__(self, locator: banshee.request.HandlerLocator, factory: banshee.request.HandlerFactory, transport: AbstractTransport) -> None:
        self.locator = locator
        self.factory = factory
        self.transport = transport

    async def __call__(self, message: banshee.message.Message[Any], handle: banshee.message.HandleMessage) -> banshee.message.Message[Any]:
        extra = {"request_class": type(message.request).__name__}
        errors = []

        serialized_message = json.dumps(message.request.dict())  # Assuming Pydantic models for requests
        await self.transport.send("my_channel", serialized_message)

        for reference in self.locator.subscribers_for(message):
            if any(context.name == reference.name for context in message.all(banshee.context.Dispatch)):
                continue

            try:
                handler = self.factory(reference)
                received_message = await self.transport.receive("my_channel")
                deserialized_request = message.request.__class__.parse_raw(received_message)
                result = await handler(deserialized_request)

                message = message.including(
                    banshee.context.Dispatch(name=reference.name, result=result,)
                )
            except Exception as error:  # pylint: disable=broad-except
                errors.append(error)

        if not message.has(banshee.context.Dispatch) and not errors:
            banshee.logger.info("no handlers for %(request_class)s found.", extra=extra)

        if errors:
            raise banshee.errors.DispatchError(f"handling {extra['request_class']} failed.", errors)

        return await handle(message)