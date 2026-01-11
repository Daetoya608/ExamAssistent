from loguru import logger
from typing import List

from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, desc, asc

from app.infrastructure.persistence.postgres.modules._base.base_repository import CRUDRepository
from app.domains.chats.schemas import ChatRead, ChatCreate, ChatUpdate, MessageRead, MessageCreate, MessageUpdate
from app.domains.chats.repo_interface import ChatRepositoryInterface, MessageRepositoryInterface
from app.infrastructure.persistence.postgres.modules.chats.models import Chat, Message


class SqlChatRepository(CRUDRepository[Chat, ChatRead, ChatCreate, ChatUpdate], ChatRepositoryInterface):

    def __init__(self, session: AsyncSession | Session):
        super().__init__(
            session=session,
            db_model=Chat,
            domain_model=ChatRead
        )
        self._chat_model = Chat
        self._message_model = Message


    async def add_message(self, message: MessageCreate) -> MessageRead:
        """Добавляет сообщение в базу данных асинхронно."""
        db_message = self._message_model(**message.model_dump())
        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return MessageRead.model_validate(db_message)


    async def get_last_messages(self, chat_id: int, context_length: int) -> List[MessageRead]:
        query = self._get_messages_with_limit_query(chat_id, context_length)
        result = await self.session.execute(query)
        # SQLAlchemy вернет строки подзапроса, нам нужно смапить их на модель сообщений
        return [MessageRead.model_validate(msg) for msg in result.scalars().all()]


    def add_message_sync(self, message: MessageCreate) -> MessageRead:
        """Добавляет сообщение в базу данных синхронно."""
        db_message = self._message_model(**message.model_dump())
        self.session.add(db_message)
        self.session.commit()
        self.session.refresh(db_message)
        return MessageRead.model_validate(db_message)


    def get_last_messages_sync(self, chat_id: int, context_length: int) -> List[MessageRead]:
        logger.info(f"chat_id: {chat_id}, context_length: {context_length}")
        query = self._get_messages_with_limit_query(chat_id, context_length)
        result = self.session.execute(query)
        logger.info(f"result: {result}")

        all_messages = result.scalars().all()
        logger.info(f"len = {len(all_messages)}")

        for msg in all_messages:
            logger.info(f"msg: {msg}")

        res = [MessageRead.model_validate(msg) for msg in all_messages]

        logger.info(f"res: {res}")
        return res

    def _get_messages_with_limit_query(self, chat_id: int, context_length: int):
        # ... (ваши пункты 1 и 2 без изменений) ...
        msg_len = func.length(func.coalesce(self._message_model.text, ""))
        cumulative_len = func.sum(msg_len).over(
            partition_by=self._message_model.chat_id,
            order_by=desc(self._message_model.id)
        ).label("running_total")

        # 3. Создаем подзапрос
        subquery = (
            select(
                self._message_model,  # Здесь выбираются все колонки модели
                cumulative_len
            )
            .filter(self._message_model.chat_id == chat_id)
            .subquery()
        )

        # !!! ВАЖНО: Создаем алиас модели, который "смотрит" на подзапрос
        msg_alias = aliased(self._message_model, subquery)

        # 4. Выбираем алиас модели, а не просто subquery
        return (
            select(msg_alias)
            .filter(subquery.c.running_total <= context_length)
            .order_by(asc(subquery.c.id))
        )


class SqlMessageRepository(CRUDRepository[Message, MessageRead, MessageCreate, MessageUpdate], MessageRepositoryInterface):

    def __init__(self, session: AsyncSession | Session):
        super().__init__(
            session=session,
            db_model=Message,
            domain_model=MessageRead
        )
