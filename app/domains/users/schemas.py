from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.domains._base.schemas import BaseSchema

class UserBase(BaseModel):
    nickname: Annotated[str, Field(default=None, description="имя пользователя")]
    username: Annotated[str, Field(description="Уникальное имя пользователя")]


class UserCreate(UserBase):
    pass


class UserRead(BaseSchema, UserBase):
    pass


class UserUpdate(BaseModel):
    nickname: Annotated[str, Field(default=None)]
    username: Annotated[str, Field(default=None)]
