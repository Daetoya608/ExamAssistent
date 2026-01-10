from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.persistence.postgres.connection.session import get_sync_session
from app.application.use_cases.upload_document import UploadDocumentUseCase
from app.infrastructure.persistence.postgres.modules.users.repository import SqlUserRepository
from app.infrastructure.persistence.postgres.modules.documents.repository import SqlDocumentRepository
from app.infrastructure.file_storage.s3.backblaze_storage import BackblazeStorage
from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF
from app.domains.users.schemas import UserRead
from app.domains.users.service import UserService
from app.domains.documents.service import DocumentService
from app.domains.vector_db.service import VectorDBService
from app.domains.storage.service import StorageService


def get_user():
    return UserRead(
        id=2,
        username="daetoya",
        nickname="zero",
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


def get_mock_user() -> UserRead:
    return UserRead(
        id=1,
        username="admin",
        nickname="nick",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )