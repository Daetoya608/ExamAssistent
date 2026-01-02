from datetime import datetime
from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    id: Annotated[int | UUID, Field(description="id объекта")]
    created_at: Annotated[datetime, Field(description="Время создания")]
    updated_at: Annotated[datetime, Field(description="Время последнего изменения")]
