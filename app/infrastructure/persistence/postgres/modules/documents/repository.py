from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domains.documents.schemas import DocumentRead, DocumentCreate, DocumentUpdate
from app.domains.documents.repo_interface import DocumentRepositoryInterface
from app.infrastructure.persistence.postgres.modules._base.base_repository import CRUDRepository
from app.infrastructure.persistence.postgres.modules.documents.models import Document


class SqlDocumentRepository(
    CRUDRepository[Document, DocumentRead, DocumentCreate, DocumentUpdate],
    DocumentRepositoryInterface
):
    def __init__(self, session: AsyncSession | Session):
        super().__init__(
            session=session,
            db_model=Document,
            domain_model=DocumentRead
        )


    async def get_by_key(self, key: str) -> DocumentRead | None:
        query = select(self.db_model).where(self.db_model.key == key)
        result = await self.session.execute(query)
        db_obj = result.scalar_one_or_none()

        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None


    async def get_user_documents(self, user_id: int) -> list[DocumentRead]:
        query = select(self.db_model).where(self.db_model.user_id == user_id)
        result = await self.session.execute(query)

        db_objs = result.scalars().all()
        return [self.domain_model.model_validate(obj) for obj in db_objs]


    def get_by_key_sync(self, key: str) -> DocumentRead | None:
        query = select(self.db_model).where(self.db_model.key == key)
        db_obj = self.session.execute(query).scalar_one_or_none()

        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None


    def get_user_documents_sync(self, user_id: int) -> list[DocumentRead]:
        query = select(self.db_model).where(self.db_model.user_id == user_id)
        db_objs = self.session.execute(query).scalars().all()

        return [self.domain_model.model_validate(obj) for obj in db_objs]
