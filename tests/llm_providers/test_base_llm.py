import pytest
from chat_app.llm_providers.base_llm import BaseLLM


# def test_base_llm_generate_not_implemented():
#     class DummyLLM(BaseLLM):
#         pass
#
#     llm = DummyLLM()
#     with pytest.raises(NotImplementedError):
#         llm.generate("Hello", "client1")
