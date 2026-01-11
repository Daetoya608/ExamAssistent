from abc import ABC, abstractmethod
from typing import List, Sequence

from langchain_core.prompt_values import PromptValue
from langchain_core.messages import AIMessage

from app.domains.chats.schemas import MessageInput


class LLMInterface(ABC):
    @abstractmethod
    def invoke(self, prompt: PromptValue | List[MessageInput] | str | Sequence[str]) -> str: ...
