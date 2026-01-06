from typing import List

from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
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
        query = self._get_messages_with_limit_query(chat_id, context_length)
        result = self.session.execute(query)
        return [MessageRead.model_validate(msg) for msg in result.scalars().all()]


    def _get_messages_with_limit_query(self, chat_id: int, context_length: int):
        """
        Вспомогательный метод для создания запроса с оконной функцией.
        """
        # 1. Вычисляем длину каждого сообщения (обрабатываем возможный None через coalesce)
        msg_len = func.length(func.coalesce(self._message_model.text, ""))

        # 2. Оконная функция: считаем накопительную сумму длин, идя от новых к старым
        cumulative_len = func.sum(msg_len).over(
            partition_by=self._message_model.chat_id,
            order_by=desc(self._message_model.id)
        ).label("running_total")

        # 3. Создаем подзапрос, где для каждого сообщения уже посчитана его "позиция" в лимите
        subquery = (
            select(
                self._message_model,
                cumulative_len
            )
            .filter(self._message_model.chat_id == chat_id)
            .subquery()
        )

        # 4. Основной запрос: выбираем только те строки, где сумма не превысила порог
        # И возвращаем их в правильном хронологическом порядке (ASC)
        return (
            select(subquery)
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
