from abc import ABC, abstractmethod

from app.domains.chats.service import ChatService
from app.domains.llm.interface import LLMInterface
from app.domains.vector_db.service import VectorDBService


class AgentInterface(ABC):
    @abstractmethod
    def process_sync(self, user_id: int, chat_service: ChatService, llm: LLMInterface,
                     vector_db_service: VectorDBService,) -> str:
        """Основной вход в агента"""
        pass
