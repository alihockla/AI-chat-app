import logging
from openai import OpenAI
from chat_app.config import config
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OllamaLLM(BaseLLM):
    def __init__(self, chat_manager):
        super().__init__(chat_manager)
        logger.info(
            f"Using Ollama provider at '{config.openai_api_url}', and LLM: {config.llm_model}"
        )
        self.client = OpenAI(base_url=config.openai_api_url)

    async def generate(self, new_user_message: str, client_id: str) -> str:
        # fetch the chat history for this client to send to the LLM for conversational context
        history = self.chat_manager.get_history(client_id)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly chatbot. Respond naturally, considering the full conversation."
                ),
            }
        ]
        for role, content in history:
            role_mapped = "user" if role == "user" else "assistant"
            messages.append({"role": role_mapped, "content": content})
        messages.append({"role": "user", "content": new_user_message})

        try:
            response = self.client.chat.completions.create(
                model=config.llm_model, messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ollama LLM error: {e}")
            return "Sorry, I had trouble responding. Can you repeat that?"
