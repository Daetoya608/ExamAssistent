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
            text=message.text
        )
        return await self.chat_repo.add_message(message_create)


    def add_messages_sync(self, message: MessageInput) -> MessageRead:
        message_create = MessageCreate(
            chat_id=self.chat_id,
            text=message.text
        )
        return self.chat_repo.add_message_sync(message_create)
