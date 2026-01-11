from sqlalchemy import BigInteger, String, Uuid, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.postgres.modules._base.model import BaseModel


class Chat(BaseModel):
    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=False)
    name: Mapped[str] = mapped_column(String, nullable=True, unique=False, default=None)

    user: Mapped["User"] = relationship(back_populates="chats")
    messages: Mapped["Message"] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class Message(BaseModel):
    __tablename__ = "messages"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False, unique=False)
    text: Mapped[str] = mapped_column(String, nullable=True, unique=False, default="")
    author: Mapped[str] = mapped_column(String, nullable=False, unique=False)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
