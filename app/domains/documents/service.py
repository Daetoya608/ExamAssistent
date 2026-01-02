from pathlib import Path

import pymupdf
from pydantic import ValidationError
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config.utils import get_settings
from app.domains.documents.schemas import PDFBase, ChunkBase


class DocumentService:

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, text_splitter = None):
        if text_splitter is None:
            settings = get_settings()
            if chunk_size is None: chunk_size = settings.CHUNK_SIZE
            if chunk_overlap is None: chunk_overlap = settings.CHUNK_OVERLAP
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._text_splitter = text_splitter


    def _divide_page_into_chunks(self, pdf_model: PDFBase, page_index) -> list[ChunkBase]:
        chunks = list()
        texts = self._text_splitter.split_text(pdf_model.pages[page_index].content)
        for chunk_index, chunk_text in enumerate(texts):
            chunk_model = ChunkBase(
                content=chunk_text,
                file_id=None,
                source=pdf_model.pages[page_index].metadata.source,
                page_num=pdf_model.pages[page_index].metadata.page,
                chunk_index=chunk_index,
            )
            chunks.append(chunk_model)
        return chunks


    def divide_into_chunks(self, pdf_model: PDFBase) -> list[ChunkBase]:
        chunks = []
        for page_index in range(len(pdf_model.pages)):
            page_chunks = self._divide_page_into_chunks(self._text_splitter, page_index)
            chunks.extend(page_chunks)

        return chunks
