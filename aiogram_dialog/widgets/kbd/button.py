from typing import Awaitable, Callable, Dict, List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton, WebAppInfo

from aiogram_dialog.api.internal import InternalDialogManager
from aiogram_dialog.api.protocols import ActiveDialogManager, DialogProtocol
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)
from .base import Keyboard
from ..when import WhenCondition

OnClick = Callable[[CallbackQuery, "Button", ActiveDialogManager], Awaitable]


class Button(Keyboard):
    def __init__(
            self,
            text: Text,
            id: str,
            on_click: Union[OnClick, WidgetEventProcessor, None] = None,
            when: WhenCondition = None,
    ):
        super().__init__(id, when)
        self.text = text
        self.on_click = ensure_event_processor(on_click)

    async def _process_own_callback(
            self,
            c: CallbackQuery,
            dialog: DialogProtocol,
            manager: InternalDialogManager,
    ) -> bool:
        await self.on_click.process_event(c, self, manager)
        return True

    async def _render_keyboard(
            self,
            data: Dict,
            manager: InternalDialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    callback_data=self._own_callback_data(),
                ),
            ],
        ]


class Url(Keyboard):
    def __init__(
            self,
            text: Text,
            url: Text,
            id: Optional[str] = None,
            when: Union[str, Callable, None] = None,
    ):
        super().__init__(id, when)
        self.text = text
        self.url = url

    async def _render_keyboard(
            self,
            data: Dict,
            manager: InternalDialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    url=await self.url.render_text(data, manager),
                ),
            ],
        ]


class WebApp(Url):
    async def _render_keyboard(
            self, data: Dict, manager: InternalDialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        text = await self.text.render_text(data, manager)

        web_app_url = await self.url.render_text(data, manager)
        web_app_info = WebAppInfo(url=web_app_url)

        return [[InlineKeyboardButton(text=text, web_app=web_app_info)]]
