from typing import List

from app.domains.chats.repo_interface import (ChatRepositoryInterface,
                                              MessageRepositoryInterface)
from app.domains.chats.schemas import MessageCreate, MessageRead, MessageInput


class ChatService:

    def __init__(self, chat_repo: ChatRepositoryInterface, chat_id: int = None):
        self.chat_repo = chat_repo
        self.chat_id = chat_id


    async def add_message(self, message: MessageInput) -> MessageRead:
        message_create = MessageCreate(
            chat_id=self.chat_id,
            text=message.text,
            author=message.author,
        )
        return await self.chat_repo.add_message(message_create)


    async def get_last_messages(self, context_length: int) -> List[MessageRead]:
        result = await self.chat_repo.get_last_messages(self.chat_id, context_length)
        return result


    def add_message_sync(self, message: MessageInput) -> MessageRead:
        message_create = MessageCreate(
            chat_id=self.chat_id,
            text=message.text,
            author=message.author,
        )
        return self.chat_repo.add_message_sync(message_create)


    def get_last_messages_sync(self, context_length: int) -> List[MessageRead]:
        result = self.chat_repo.get_last_messages_sync(self.chat_id, context_length)
        return result
