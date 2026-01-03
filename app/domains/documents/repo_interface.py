from abc import abstractmethod

from app.domains._base.base_db_interface import BaseCRUDInterface
from app.domains.documents.schemas import DocumentRead, DocumentCreate, DocumentUpdate


class DocumentRepositoryInterface(BaseCRUDInterface[DocumentRead, DocumentCreate, DocumentUpdate]):
    @abstractmethod
    async def get_by_key(self, key: str) -> DocumentRead | None:
        pass

    @abstractmethod
    async def get_user_documents(self, user_id: int) -> list[DocumentRead]:
        pass

    @abstractmethod
    def get_by_key_sync(self, key: str) -> DocumentRead | None:
        pass

    @abstractmethod
    def get_user_documents_sync(self, user_id: int) -> list[DocumentRead]:
        pass
