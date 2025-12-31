from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(from_attributes=True)


class ChunkMetadata(BaseModel):
    file_id: Annotated[str | None, Field(default=None, description="Идентификатор файла")]
    source: Annotated[str, Field(description="Название файла")]
    page_num: Annotated[int, Field(description="Номер страницы")]
    chunk_index: Annotated[int, Field(description="Индекс чанка")]


class ChunkBase(BaseModel):
    content: Annotated[str, Field(description="Текст чанка")]
    metadata: Annotated[ChunkMetadata, Field(description="Метаданные чанка")]
