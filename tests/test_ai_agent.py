import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from chat_app.ai_agent import AIAgent


@pytest.mark.asyncio
async def test_ai_agent_run_processes_one_message(mock_chat_manager, mock_ollama_llm, mocker):
    event_bus = asyncio.Queue()

    # setup mocks
    mock_ollama_llm.generate = AsyncMock(return_value="Response from AI")
    mock_chat_manager.store_message = Mock()

    # create the agent
    agent = AIAgent(event_bus=event_bus, chat_manager=mock_chat_manager, llm=mock_ollama_llm)

    # start agent in background
    task = asyncio.create_task(agent.run())

    # put a message into the event bus for processing
    await event_bus.put(("client1", "hello"))

    # wait for the event to be processed
    await asyncio.sleep(0.1)

    mock_ollama_llm.generate.assert_awaited_once_with("hello", "client1")
    mock_chat_manager.store_message.assert_called_once_with("client1", "ai", "Response from AI")

    # stop the agent
    agent.stop()
