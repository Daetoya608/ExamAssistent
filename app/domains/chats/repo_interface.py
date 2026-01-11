from abc import ABC, abstractmethod
from typing import List

from app.domains._base.base_db_interface import BaseCRUDInterface
from app.domains.chats.schemas import MessageCreate, ChatCreate, ChatRead, ChatUpdate, MessageRead, MessageUpdate


class ChatRepositoryInterface(BaseCRUDInterface[ChatRead, ChatCreate, ChatUpdate]):
    @abstractmethod
    async def add_message(self, message: MessageCreate) -> MessageRead: ...

    @abstractmethod
    async def get_last_messages(self, chat_id: int, context_length: int) -> List[MessageRead]: ...

    @abstractmethod
    def add_message_sync(self, message: MessageCreate) -> MessageRead: ...

    @abstractmethod
    def get_last_messages_sync(self, chat_id: int, context_length: int) -> List[MessageRead]: ...



class MessageRepositoryInterface(BaseCRUDInterface[MessageRead, MessageCreate, MessageUpdate]):
    pass
