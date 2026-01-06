from typing import Annotated

from pydantic import BaseModel, Field

from app.domains._base.schemas import BaseSchema


class ChatBase(BaseSchema):
    user_id: Annotated[int, Field(description="ID владельца чата")]
    name: Annotated[str | None, Field(default=None, description="Название чата")]


class ChatCreate(ChatBase):
    pass


class ChatRead(BaseSchema, ChatBase):
    pass


class ChatUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, description="Обновленное название чата")]


class MessageInput(BaseModel):
    text: Annotated[str, Field(description="Текст сообщения")]
    author: Annotated[str, Field(description="Автор сообщения")]


class MessageBase(MessageInput):
    chat_id: Annotated[int, Field(description="ID чата, кот-му принадлежит сообщение")]


class MessageCreate(MessageBase):
    pass


class MessageRead(BaseSchema, MessageBase):
    pass


class MessageUpdate(MessageBase):
    text: Annotated[str | None, Field(default=None, description="Обновленное сообщение")]
