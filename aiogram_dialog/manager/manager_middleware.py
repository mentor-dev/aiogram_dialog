from typing import Any, Awaitable, Callable, Dict, Union

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

from aiogram_dialog.api.entities import ChatEvent, DialogUpdateEvent
from aiogram_dialog.api.internal import (
    DialogManagerFactory, InternalDialogManager,
)
from aiogram_dialog.api.protocols import DialogRegistryProtocol

MANAGER_KEY = "dialog_manager"


class ManagerMiddleware(BaseMiddleware):
    def __init__(
            self,
            registry: DialogRegistryProtocol,
            dialog_manager_factory: DialogManagerFactory,
    ):
        super().__init__()
        self.registry = registry
        self.dialog_manager_factory = dialog_manager_factory

    async def __call__(
            self,
            handler: Callable[
                [Union[Update, DialogUpdateEvent], Dict[str, Any]],
                Awaitable[Any],
            ],
            event: ChatEvent,
            data: Dict[str, Any],
    ) -> Any:
        data[MANAGER_KEY] = self.dialog_manager_factory(
            event=event,
            registry=self.registry,
            data=data,
        )

        try:
            return await handler(event, data)
        finally:
            manager: InternalDialogManager = data.pop(MANAGER_KEY, None)
            if manager:
                await manager.close_manager()
