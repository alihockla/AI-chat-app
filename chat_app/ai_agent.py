import logging
import asyncio

from .chat_manager import ChatManager
from .llm_providers.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class AIAgent:
    """Mock AI agent that listens for messages and replies."""

    def __init__(
        self, event_bus: asyncio.Queue, chat_manager: ChatManager, llm: BaseLLM
    ):
        self.event_bus = event_bus
        self.chat_manager = chat_manager
        self.llm = llm
        self._stopping = False

    async def run(self):
        while not self._stopping:
            client_id, message = await self.event_bus.get()
            logger.debug(f"Processing message from client {client_id}")

            ai_response = await self.llm.generate(message, client_id)
            print(f"response from AI: {ai_response}")

            self.chat_manager.store_message(client_id, "ai", ai_response)
            await self.chat_manager.send_live_message(client_id, "ai", ai_response)

    def stop(self) -> None:
        self._stopping = True
