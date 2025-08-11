import pytest

from unittest.mock import Mock


@pytest.mark.asyncio
async def test_ollama_generate(mock_ollama_llm, mocker):
    mock_ollama_llm.chat_manager.get_history = Mock(return_value=[("user", "Hello")])
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content="Hi from Ollama"))]
    mock_ollama_llm.client.chat.completions.create.return_value = mock_response

    result = await mock_ollama_llm.generate("How are you?", "client1")
    assert result == "Hi from Ollama"
    mock_ollama_llm.chat_manager.get_history.assert_called_once_with("client1")
