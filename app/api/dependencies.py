from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.chat import ChatUseCase
from app.core.config import get_settings
from app.domains.chats.service import ChatService
from app.infrastructure.persistence.postgres.connection.session import get_sync_session
from app.application.use_cases.upload_document import UploadDocumentUseCase
from app.infrastructure.persistence.postgres.modules.chats.repository import SqlChatRepository
from app.infrastructure.persistence.postgres.modules.users.repository import SqlUserRepository
from app.infrastructure.persistence.postgres.modules.documents.repository import SqlDocumentRepository
from app.infrastructure.file_storage.s3.backblaze_storage import BackblazeStorage
from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
from app.infrastructure.openai_llm.langchain_openai_repo import OpenAIRepository
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF
from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
from app.infrastructure.langgraph_agent.agent import LangGraphAIAgent
from app.domains.users.schemas import UserRead
from app.domains.users.service import UserService
from app.domains.documents.service import DocumentService
from app.domains.vector_db.service import VectorDBService
from app.domains.storage.service import StorageService
from app.domains.chats.schemas import ChatRead


def get_user():
    return UserRead(
        id=2,
        username="daetoya",
        nickname="zero",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def get_chat(user: UserRead = Depends(get_user)):
    return ChatRead(
        id=1,
        user_id=user.id,
        name="first",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def get_upload_document_use_case(
        session: Session = Depends(get_sync_session),  # Твоя сессия БД
        user: UserRead = Depends(get_user)
) -> UploadDocumentUseCase:
    # 1. Инициализируем репозитории
    user_repo = SqlUserRepository(session)
    doc_repo = SqlDocumentRepository(session)

    # 2. Инициализируем инфраструктурные сервисы
    storage = BackblazeStorage()

    vector_storage = QdrantFilesRepository()
    parser = ParserPDF()

    # 3. Инициализируем доменные сервисы
    user_service = UserService(user_repo)
    document_service = DocumentService(document_repo=doc_repo, parser=parser, user_id=user.id)
    storage_service = StorageService(storage)
    vector_db_service = VectorDBService(vector_storage=vector_storage)

    # 4. Собираем Use Case
    return UploadDocumentUseCase(
        document_service=document_service,
        storage_service=storage_service,
        user_service=user_service,
        vector_db_service=vector_db_service
    )


def get_chat_use_case(
        session: Session = Depends(get_sync_session),
        user: UserRead = Depends(get_user),
        chat: ChatRead = Depends(get_chat)
) -> ChatUseCase:

    chat_repo = SqlChatRepository(session)
    vector_repo = QdrantFilesRepository()

    user_id = user.id
    chat_service = ChatService(chat_repo=chat_repo, chat_id=chat.id)
    vector_db_service = VectorDBService(vector_storage=vector_repo)
    llm = OpenAIRepository()
    agent = LangGraphAIAgent()

    return ChatUseCase(
        user_id=user_id,
        chat_service=chat_service,
        vector_db_service=vector_db_service,
        llm=llm,
        agent=agent
    )



def get_mock_user() -> UserRead:
    return UserRead(
        id=1,
        username="admin",
        nickname="nick",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )