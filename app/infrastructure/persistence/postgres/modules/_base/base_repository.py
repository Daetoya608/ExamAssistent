from sqlalchemy import delete, select, update, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.domains._base.base_db_interface import BaseCRUDInterface
from app.domains._base.exceptions import (CreateFailedException,
                                          CreateIntegrityException,
                                          CRUDException, DeleteFailedException,
                                          NotFoundException,
                                          UpdateFailedException)


class CRUDRepository[T_DB, T_read, T_create, T_update](BaseCRUDInterface[T_read, T_create, T_update]):

    def __init__(
            self,
            session: AsyncSession | Session,
            db_model: type[T_DB],
            domain_model: type[T_read],
    ):
        self.session = session
        self.db_model = db_model
        self.domain_model = domain_model

    # -------------------- #
    #   Async CRUD         #
    # -------------------- #

    async def create(self, create_instance: T_create) -> T_read:
        try:
            data = create_instance.model_dump() if hasattr(create_instance, 'model_dump') else create_instance
            db_obj = self.db_model(**data)

            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return self.domain_model.model_validate(db_obj)
        except IntegrityError as e:
            await self.session.rollback()
            raise CreateIntegrityException(f"Database integrity error: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise CreateFailedException(f"Failed to create entity: {str(e)}")


    async def get_by_id(self, id: int) -> T_read | None:
        try:
            db_obj = await self.session.get(self.db_model, id)
            if not db_obj:
                return None
            return self.domain_model.model_validate(db_obj)
        except SQLAlchemyError as e:
            raise CRUDException(f"Error fetching entity by id {id}: {str(e)}")


    async def update(self, id: int, update_instance: T_update) -> T_read:
        try:
            db_obj = await self.session.get(self.db_model, id)
            if not db_obj:
                raise NotFoundException(f"Entity with id {id} not found")

            update_data = update_instance.model_dump(exclude_unset=True) if hasattr(update_instance,
                                                                                    'model_dump') else update_instance

            for key, value in update_data.items():
                setattr(db_obj, key, value)

            await self.session.commit()
            await self.session.refresh(db_obj)
            return self.domain_model.model_validate(db_obj)
        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise UpdateFailedException(f"Failed to update entity {id}: {str(e)}")


    async def delete(self, id: int) -> None:
        try:
            db_obj = await self.session.get(self.db_model, id)
            if not db_obj:
                raise NotFoundException(f"Entity with id {id} not found")

            await self.session.delete(db_obj)
            await self.session.commit()
        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DeleteFailedException(f"Failed to delete entity {id}: {str(e)}")

    # -------------------- #
    #   Sync CRUD          #
    # -------------------- #

    def create_sync(self, create_instance: T_create) -> T_read:
        try:
            data = create_instance.model_dump() if hasattr(create_instance, 'model_dump') else create_instance
            db_obj = self.db_model(**data)
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
            return self.domain_model.model_validate(db_obj)
        except IntegrityError as e:
            self.session.rollback()
            raise CreateIntegrityException(str(e))
        except Exception as e:
            self.session.rollback()
            raise CreateFailedException(str(e))


    def get_by_id_sync(self, id: int) -> T_read | None:
        try:
            db_obj = self.session.get(self.db_model, id)
            return self.domain_model.model_validate(db_obj) if db_obj else None
        except SQLAlchemyError as e:
            raise CRUDException(f"Error fetching entity by id {id}: {str(e)}")


    def update_sync(self, id: int, update_instance: T_update) -> T_read:
        try:
            db_obj = self.session.get(self.db_model, id)
            if not db_obj:
                raise NotFoundException()

            update_data = update_instance.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_obj, key, value)

            self.session.commit()
            self.session.refresh(db_obj)
            return self.domain_model.model_validate(db_obj)
        except NotFoundException:
            raise
        except Exception as e:
            self.session.rollback()
            raise UpdateFailedException(f"Failed to update entity {id}: {str(e)}")


    def delete_sync(self, id: int) -> None:
        try:
            db_obj = self.session.get(self.db_model, id)
            if not db_obj:
                raise NotFoundException()
            self.session.delete(db_obj)
            self.session.commit()
        except NotFoundException:
            raise
        except Exception as e:
            self.session.rollback()
            raise DeleteFailedException(f"Failed to delete entity {id}: {str(e)}")
