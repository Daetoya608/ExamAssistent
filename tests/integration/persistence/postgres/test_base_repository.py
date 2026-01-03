import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, create_mock_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pydantic import BaseModel, ConfigDict

from app.domains._base.exceptions import NotFoundException, CreateIntegrityException
from app.infrastructure.persistence.postgres.modules._base.base_repository import CRUDRepository

# --- Схемы и Модели для тестов ---
Base = declarative_base()


class MockUserTable(Base):
    __tablename__ = "test_users"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String)


class MockUserRead(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)  # Важно для model_validate


class MockUserCreate(BaseModel):
    name: str
    email: str


class MockUserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


# --- Фикстуры для базы данных ---
@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLoom = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLoom() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def repo(async_session):
    return CRUDRepository[MockUserTable, MockUserRead, MockUserCreate, MockUserUpdate](
        session=async_session,
        db_model=MockUserTable,
        domain_model=MockUserRead
    )


@pytest.mark.asyncio
async def test_create_success(repo):
    user_in = MockUserCreate(name="John", email="john@example.com")
    result = await repo.create(user_in)

    assert result.id is not None
    assert result.name == "John"
    assert isinstance(result, MockUserRead)


@pytest.mark.asyncio
async def test_create_integrity_error(repo):
    user_in = MockUserCreate(name="John", email="john@example.com")
    await repo.create(user_in)

    # Повторный инсерт того же имени (unique=True)
    with pytest.raises(CreateIntegrityException):
        await repo.create(user_in)


@pytest.mark.asyncio
async def test_get_by_id_found(repo):
    user_in = MockUserCreate(name="Alice", email="alice@example.com")
    created = await repo.create(user_in)

    found = await repo.get_by_id(created.id)
    assert found.id == created.id
    assert found.name == "Alice"


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo):
    found = await repo.get_by_id(999)
    assert found is None


@pytest.mark.asyncio
async def test_update_partial(repo):
    created = await repo.create(MockUserCreate(name="Old", email="old@ex.com"))

    # Обновляем только email
    update_data = MockUserUpdate(email="new@ex.com")
    updated = await repo.update(created.id, update_data)

    assert updated.email == "new@ex.com"
    assert updated.name == "Old"  # Имя не должно измениться


@pytest.mark.asyncio
async def test_delete_success(repo):
    created = await repo.create(MockUserCreate(name="To Delete", email="d@ex.com"))
    await repo.delete(created.id)

    found = await repo.get_by_id(created.id)
    assert found is None


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def sync_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLoom = sessionmaker(bind=engine)
    session = SessionLoom()
    yield session
    session.close()

@pytest.fixture
def sync_repo(sync_session):
    return CRUDRepository[MockUserTable, MockUserRead, MockUserCreate, MockUserUpdate](
        session=sync_session,
        db_model=MockUserTable,
        domain_model=MockUserRead
    )

def test_create_sync(sync_repo):
    user_in = MockUserCreate(name="SyncUser", email="s@ex.com")
    result = sync_repo.create_sync(user_in)
    assert result.name == "SyncUser"

def test_update_sync_not_found(sync_repo):
    with pytest.raises(NotFoundException):
        sync_repo.update_sync(999, MockUserUpdate(name="None"))
