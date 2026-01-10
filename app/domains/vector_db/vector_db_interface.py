from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.documents.schemas import ChunkBase


class VectorDBInterface(ABC):

    @abstractmethod
    def init_storage(self) -> None:
        """Инициализация: создание коллекции и индексов"""
        pass

    @abstractmethod
    def upsert_batches(self, chunks: List[ChunkBase]) -> None:
        """Массовая загрузка чанков"""
        pass

    @abstractmethod
    def search(
            self,
            query_text: str,
            user_id: int,
            top_k: int = 5,
            file_id: Optional[str] = None
    ) -> List[ChunkBase]:
        """Поиск с опциональной фильтрацией по файлу"""
        pass

    @abstractmethod
    def delete_by_file_id(self, file_id: str) -> None:
        """Удаление всех данных конкретного документа"""
        pass

    @abstractmethod
    def get_all_files(self) -> List[str]:
        """Список всех уникальных файлов в индексе (через метаданные)"""
        pass
