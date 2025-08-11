import pytest
from unittest.mock import AsyncMock, Mock
from chat_app.database.database import Database
from chat_app.llm_providers.ollama_llm import OllamaLLM
from chat_app.llm_providers.openai_llm import OpenAIResponsesLLM
from chat_app.chat_manager import ChatManager


@pytest.fixture
def memory_db():
    """In-memory database for testing."""
    db = Database(":memory:")
    db.start()
    yield db
    db.stop()


@pytest.fixture
def mock_chat_manager(memory_db):
    """ChatManager with in-memory DB."""
    cm = ChatManager(db=memory_db)
    return cm


@pytest.fixture
def mock_ollama_llm(mock_chat_manager, mocker):
    """Ollama LLM with mocked OpenAI API client."""
    llm = OllamaLLM(chat_manager=mock_chat_manager)
    llm.client = Mock()
    return llm


@pytest.fixture
def mock_openai_llm(mock_chat_manager, mocker):
    """OpenAIResponsesLLM with mocked OpenAI API client."""
    llm = OpenAIResponsesLLM(chat_manager=mock_chat_manager)
    llm.client = Mock()
    return llm
