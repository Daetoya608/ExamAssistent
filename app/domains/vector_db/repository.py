from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VectorDBRepository(ABC):

    @abstractmethod
    async def init_storage(self) -> None:
        """Инициализация: создание коллекции и индексов"""
        pass

    @abstractmethod
    async def upsert_batches(self, chunks: List[Any], embeddings: List[List[float]]) -> None:
        """Массовая загрузка чанков"""
        pass

    @abstractmethod
    async def search(
            self,
            query_vector: List[float],
            top_k: int = 5,
            file_id: Optional[str] = None
    ) -> List[Any]:
        """Поиск с опциональной фильтрацией по файлу"""
        pass

    @abstractmethod
    async def delete_by_file_id(self, file_id: str) -> None:
        """Удаление всех данных конкретного документа"""
        pass

    @abstractmethod
    async def get_all_files(self) -> List[str]:
        """Список всех уникальных файлов в индексе (через метаданные)"""
        pass
