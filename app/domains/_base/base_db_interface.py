from abc import ABC, abstractmethod


class BaseCRUDInterface[T_read, T_create, T_update](ABC):
    @abstractmethod
    async def create(self, create_instance: T_create) -> T_read: ...

    @abstractmethod
    async def get_by_id(self, id: int) -> T_read | None: ...

    @abstractmethod
    async def update(self, id: int, update_instance: T_update) -> T_read: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...

    @abstractmethod
    def create_sync(self, create_instance: T_create) -> T_read: ...

    @abstractmethod
    def get_by_id_sync(self, id: int) -> T_read | None: ...

    @abstractmethod
    def update_sync(self, id: int, update_instance: T_update) -> T_read: ...

    @abstractmethod
    def delete_sync(self, id: int) -> None: ...
