from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.infrastructure.persistence.postgres import Base


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def get_sync_session_maker(self) -> sessionmaker:
        sync_uri = get_settings().database_uri_sync
        sync_engine = create_engine(sync_uri, echo=False, future=True)
        return sessionmaker(sync_engine, class_=Session, expire_on_commit=False)

    def refresh(self) -> None:
        self.engine = create_async_engine(
            get_settings().database_uri, echo=True, future=True
        )


async def init_models() -> None:
    """
    Создаёт все таблицы в базе данных, если их ещё нет.
    """

    engine = SessionManager().engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы успешно созданы (или уже существовали).")


async def get_session() -> AsyncIterator[AsyncSession]:
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session


def get_sync_session() -> Session:
    session_maker = SessionManager().get_sync_session_maker()
    session = session_maker()
    return session


__all__ = [
    "get_session",
    "get_sync_session",
    "SessionManager",
]