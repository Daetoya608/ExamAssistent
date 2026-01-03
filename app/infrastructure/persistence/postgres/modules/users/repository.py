from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domains.users.schemas import UserRead, UserCreate, UserUpdate
from app.domains.users.repo_interface import UserRepositoryInterface
from app.infrastructure.persistence.postgres.modules._base.base_repository import CRUDRepository
from app.infrastructure.persistence.postgres.modules.users.models import User


class SqlUserRepository(CRUDRepository[User, UserRead, UserCreate, UserUpdate], UserRepositoryInterface):

    def __init__(self, session: AsyncSession | Session):
        super().__init__(
            session=session,
            db_model=User,
            domain_model=UserRead
        )


    async def get_by_username(self, username: str) -> UserRead | None:
        query = select(self.db_model).where(self.db_model.username == username)
        result = await self.session.execute(query)
        db_obj = result.scalar_one_or_none()

        if db_obj:
            return self.domain_model.model_validate(db_obj)

        return None


    def get_by_username_sync(self, username: str) -> UserRead | None:
        db_obj = self.session.execute(
            select(self.db_model).where(self.db_model.username == username)
        ).scalar_one_or_none()

        return self.domain_model.model_validate(db_obj) if db_obj else None
