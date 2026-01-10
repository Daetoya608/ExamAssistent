from typing import List, Sequence

from langchain_core.prompt_values import PromptValue
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.config.utils import get_settings
from app.domains.chats.schemas import MessageInput, AuthorRole
from app.domains.llm.interface import LLMInterface


class OpenAIRepository(LLMInterface):
    def __init__(self):
        self.model = self._get_model_name()
        self.llm = self._get_llm(self.model)


    def invoke(self, prompt: PromptValue | List[MessageInput] | str | Sequence[str]) -> str:
        # messages = self._create_standard_messages(prompt)
        response = self.llm.invoke(prompt)
        if isinstance(response.content, str):
            return response.content
        if isinstance(response.content, list):
            return "".join([block["text"] for block in response.content if isinstance(block, dict) and "text" in block])
        return str(response.content)


    def _get_model_name(self) -> str:
        settings = get_settings()
        return settings.OPENAI_MODEL


    def _get_llm(self, model: str):
        llm = ChatOpenAI(model=model)
        return llm


    def _create_standard_messages(self, messages: List[MessageInput]) -> List[BaseMessage]:
        result_messages = []
        for message in messages:
            if message.author == AuthorRole.HUMAN:
                result_messages.append(HumanMessage(message.message_text))
            elif message.author == AuthorRole.AI:
                result_messages.append(AIMessage(message.message_text))
            elif message.author == AuthorRole.SYSTEM:
                result_messages.append(SystemMessage(message.message_text))
        return result_messages
