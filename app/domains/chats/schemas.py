from typing import Annotated
from enum import Enum

from pydantic import BaseModel, Field

from app.domains._base.schemas import BaseSchema


class ChatBase(BaseModel):
    user_id: Annotated[int, Field(description="ID владельца чата")]
    name: Annotated[str | None, Field(default=None, description="Название чата")]


class ChatCreate(ChatBase):
    pass


class ChatRead(BaseSchema, ChatBase):
    pass


class ChatUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, description="Обновленное название чата")]


class AuthorRole(str, Enum):
    AI = "AI"
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"


class MessageUserInput(BaseModel):
    text: Annotated[str, Field(description="Текст сообщения")]


class MessageInput(MessageUserInput):
    author: Annotated[AuthorRole, Field(description="Автор сообщения")]


class MessageBase(MessageInput):
    chat_id: Annotated[int, Field(description="ID чата, кот-му принадлежит сообщение")]


class MessageCreate(MessageBase):
    pass


class MessageRead(BaseSchema, MessageBase):
    pass


class MessageUpdate(MessageBase):
    text: Annotated[str | None, Field(default=None, description="Обновленное сообщение")]
