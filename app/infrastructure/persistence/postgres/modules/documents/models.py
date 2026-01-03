from sqlalchemy import BigInteger, String, Uuid, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.postgres.modules._base.model import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=False)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String, nullable=True, unique=False)

    user: Mapped["User"] = relationship(back_populates="documents")
