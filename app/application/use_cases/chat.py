from loguru import logger

from app.domains.chats.service import ChatService
from app.domains.llm.interface import LLMInterface
from app.domains.vector_db.service import VectorDBService
from app.domains.agent.interface import AgentInterface
from app.domains.chats.schemas import MessageInput, AuthorRole


class ChatUseCase:
    def __init__(
            self,
            user_id: int,
            chat_service: ChatService,
            vector_db_service: VectorDBService,
            llm: LLMInterface,
            agent: AgentInterface,
    ):
        self.user_id = user_id
        self.chat_service = chat_service
        self.vector_db_service = vector_db_service
        self.llm = llm
        self.agent = agent


    def _chat(self, new_message: str):

        new_mes = self.chat_service.add_message_sync(
            MessageInput(text=new_message, author=AuthorRole.HUMAN)
        )
        logger.info(f"new message: {new_mes}")
        answer = self.agent.process_sync(
            user_id=self.user_id,
            chat_service=self.chat_service,
            llm=self.llm,
            vector_db_service=self.vector_db_service,
        )

        return answer

    def execute(self, new_message: str) -> str | None:
        try:
            answer = self._chat(new_message)
            return answer
        except Exception as e:
            print(f"Error!: {e}")
            return None
