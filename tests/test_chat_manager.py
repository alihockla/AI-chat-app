from unittest.mock import AsyncMock, ANY

import pytest


@pytest.mark.asyncio
async def test_chat_manager_history_in_memory(mock_chat_manager):
    client_id = "client1"
    mock_chat_manager.store_message(client_id, "user", "Hello")
    mock_chat_manager.store_message(client_id, "ai", "Hi there")

    history = mock_chat_manager.get_history(client_id)
    assert len(history) == 2
    assert history[0] == ("user", "Hello")


@pytest.mark.asyncio
async def test_chat_manager_history_from_db(mock_chat_manager):
    client_id = "client1"
    mock_chat_manager.store_message(client_id, "user", "Hello")
    mock_chat_manager.store_message(client_id, "ai", "Hi there")

    # clear in-memory history to force DB read
    mock_chat_manager.chat_history.pop(client_id)

    history = mock_chat_manager.get_history(client_id)
    assert len(history) == 2
    assert history[0] == ("user", "Hello")


@pytest.mark.asyncio
async def test_chat_manager_websocket(mock_chat_manager, mocker):
    mock_ws = AsyncMock()
    client_id = "client1"

    await mock_chat_manager.connect(client_id, mock_ws)
    assert client_id in mock_chat_manager.active_connections

    mock_chat_manager.disconnect(client_id)
    assert client_id not in mock_chat_manager.active_connections


@pytest.mark.asyncio
async def test_send_live_message(mock_chat_manager, mocker):
    client_id = "client1"
    message = "Test live message"
    mock_ws = AsyncMock()

    # connect to  register the websocket
    await mock_chat_manager.connect(client_id, mock_ws)

    await mock_chat_manager.send_live_message(client_id, "test-user", message)

    mock_ws.send_text.assert_awaited_with(f"MESSAGE::test-user: {message}")


@pytest.mark.asyncio
async def test_get_last_response_id_and_save_last_response_id(mock_chat_manager):
    client_id = "client1"
    # Initially, there should be no last response id
    assert mock_chat_manager.get_last_response_id(client_id) is None

    # Save a last response id
    last_id = "response_123"
    mock_chat_manager.save_last_response_id(client_id, last_id)

    # Now, get_last_response_id should return the saved id
    assert mock_chat_manager.get_last_response_id(client_id) == last_id
