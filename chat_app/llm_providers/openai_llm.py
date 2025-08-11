import logging
from openai import OpenAI
from chat_app.config import config
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OpenAIResponsesLLM(BaseLLM):
    def __init__(self, chat_manager):
        super().__init__(chat_manager)
        logger.info(f"Using OpenAI provider with LLM: {config.llm_model}")
        self.client = OpenAI(api_key=config.openai_api_key)

    async def generate(self, new_user_message: str, client_id: str) -> str:
        # retrieve last_response_id stored in the DB
        last_response_id = self.chat_manager.get_last_response_id(client_id)
        try:
            if last_response_id:
                logger.info("Previous response found, continuing conversation.")
                resp = self.client.responses.create(
                    model=config.llm_model,
                    previous_response_id=last_response_id,
                    input=[{"role": "user", "content": new_user_message}],
                )
            else:
                logger.info("No previous response found, generating new response.")
                resp = self.client.responses.create(
                    model=config.llm_model,
                    input=[
                        {"role": "system", "content": "You are a friendly chatbot."},
                        {"role": "user", "content": new_user_message},
                    ],
                )

            ai_response = resp.output_text
            self.chat_manager.save_last_response_id(client_id, resp.id)

            logger.info(f"AI response for client {client_id}: {ai_response}")
            return ai_response
        except Exception as e:
            logger.error(f"OpenAI Responses API error: {e}")
            return "Sorry, I had trouble responding. Can you repeat that?"
