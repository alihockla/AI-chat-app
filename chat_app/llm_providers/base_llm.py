class BaseLLM:
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager

    async def generate(self, new_user_message: str, client_id: str) -> str:
        """
        Generate a response from the LLM. The LLM implementation can fetch any data it needs (history, last_response_id)
        via the chat_manager.

        :param new_user_message: The latest user message to respond to.
        :param client_id: The ID of the client making the request, used to fetch data from the database.
        :return: The assistant's reply as a string.
        """
        raise NotImplementedError
