from abc import abstractmethod

from app.domains._base.base_db_interface import BaseCRUDInterface
from app.domains.users.schemas import UserRead, UserCreate, UserUpdate


class UserRepositoryInterface(BaseCRUDInterface[UserRead, UserCreate, UserUpdate]):
    @abstractmethod
    async def get_by_username(self, username: str) -> UserRead | None:
        pass

    @abstractmethod
    def get_by_username_sync(self, username: str) -> UserRead | None:
        pass
