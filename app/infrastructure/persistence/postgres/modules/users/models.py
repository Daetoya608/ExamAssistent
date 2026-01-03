from typing import List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.postgres.modules._base.model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    nickname: Mapped[str] = mapped_column(String, nullable=True, unique=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    documents: Mapped[List["Document"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
