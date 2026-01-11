from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.domains._base.schemas import BaseSchema


class Metadata(BaseModel):
    source: Annotated[str, Field(description="Название исходного файла")]
    page: Annotated[int, Field(gt=0, description="Номер страницы (начиная с 1)")]

    model_config = ConfigDict(from_attributes=True)


class PDFPage(BaseModel):
    content: Annotated[str, Field(min_length=1, description="Текстовое содержимое страницы")]
    metadata: Annotated[Metadata, Field(description="Метаданные страницы")]

    model_config = ConfigDict(from_attributes=True)


class PDFBase(BaseModel):
    pages: Annotated[list[PDFPage], Field(default_factory=list, description="Списки страниц")]
    file_id: Annotated[str, Field(default=None, description="Идентификатор документа")]

    model_config = ConfigDict(from_attributes=True)


class ChunkMetadata(BaseModel):
    user_id: Annotated[int, Field(description="Идентификатор пользователя")]
    file_id: Annotated[str | None, Field(default=None, description="Идентификатор файла")]
    source: Annotated[str, Field(description="Название файла")]
    page_num: Annotated[int, Field(description="Номер страницы")]
    chunk_index: Annotated[int, Field(description="Индекс чанка")]


class ChunkBase(ChunkMetadata):
    content: Annotated[str, Field(description="Текст чанка")]


class DocumentBase(BaseModel):
    user_id: Annotated[int, Field(description="ID владельца")]
    key: Annotated[str, Field(description="Ключ документа")]
    filename: Annotated[str, Field(default=None, description="название файла")]


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(BaseSchema, DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    user_id: Annotated[int, Field(default=None)]
    key: Annotated[str, Field(default=None)]
