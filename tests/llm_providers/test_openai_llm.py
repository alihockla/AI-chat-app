import pytest

from unittest.mock import Mock


@pytest.mark.asyncio
async def test_openai_generate_with_previous_id(mock_openai_llm, mocker):
    mock_openai_llm.chat_manager.get_last_response_id = Mock(return_value="prev123")
    mock_openai_llm.chat_manager.save_last_response_id = Mock()  # prevent SQLite insert
    mock_response = mocker.Mock()
    mock_response.output_text = "Hi from OpenAI"
    mock_openai_llm.client.responses.create.return_value = mock_response
    # mocker.patch('openai.resources.responses.Responses.create', return_value=mock_response)

    result = await mock_openai_llm.generate("Tell me something", "client1")
    assert result == "Hi from OpenAI"
    mock_openai_llm.chat_manager.get_last_response_id.assert_called_once_with("client1")


# @pytest.mark.asyncio
# async def test_my_openai_function(mock_openai_llm, mocker):
#     mock_response_object = mocker.MagicMock(output=mocker.MagicMock(text="Mocked response text."))
#     mocker.patch('openai.resources.responses.create', return_value=mock_response_object)
#     # Call your function that uses openai.responses.create
#     result = await mock_openai_llm.generate("Tell me something", "client1")
#     # Assertions on the result
#     assert result == "Mocked response text."
