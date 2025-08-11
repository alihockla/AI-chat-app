from pydantic import model_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration settings
    """

    # General configuration
    index_html: str = "chat_app/templates/index.html"
    # Database configuration
    db_path: str = "chat_app/database/chat_history.db"

    # LLM provider configuration
    llm_model: str = "gpt-4o-mini"

    # OpenAI LLM provider configuration (Default)
    # must set OPENAI_API_KEY
    openai_api_key: str | None = None

    # Ollama LLM provider configuration
    use_ollama: bool = False
    openai_api_url: str = "http://localhost:11434/v1"

    # validate LLM provider configuration
    # https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    @model_validator(mode="after")
    def validate_llm_choice(self) -> "Config":
        if not self.use_ollama and not self.openai_api_key:
            raise ValueError(
                "No LLM provider configured. Either set USE_OLLAMA=True or provide OPENAI_API_KEY."
            )
        return self


config = Config()
