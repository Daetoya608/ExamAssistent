from uuid import uuid4
from pathlib import Path

import pymupdf
from pydantic import ValidationError
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config.utils import get_settings
from app.domains.documents.schemas import PDFBase, ChunkBase
from app.domains.documents.repo_interface import DocumentRepositoryInterface
from app.domains.documents.parser_interface import ParserInterface


class DocumentServiceBase:

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, text_splitter = None):
        if text_splitter is None:
            settings = get_settings()
            if chunk_size is None: chunk_size = settings.CHUNK_SIZE
            if chunk_overlap is None: chunk_overlap = settings.CHUNK_OVERLAP
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._text_splitter = text_splitter



    def _divide_page_into_chunks(self, pdf_model: PDFBase, page_index: int, user_id: int) -> list[ChunkBase]:
        chunks = list()
        texts = self._text_splitter.split_text(pdf_model.pages[page_index].content)
        for chunk_index, chunk_text in enumerate(texts):
            chunk_model = ChunkBase(
                user_id=user_id,
                content=chunk_text,
                file_id=None,
                source=pdf_model.pages[page_index].metadata.source,
                page_num=pdf_model.pages[page_index].metadata.page,
                chunk_index=chunk_index,
            )
            chunks.append(chunk_model)
        return chunks


    def _divide_into_chunks_by_user_id(self, pdf_model: PDFBase, user_id: int) -> list[ChunkBase]:
        chunks = []
        for page_index in range(len(pdf_model.pages)):
            page_chunks = self._divide_page_into_chunks(pdf_model, page_index, user_id)
            chunks.extend(page_chunks)

        return chunks


class DocumentService(DocumentServiceBase):
    def __init__(
            self,
            document_repo: DocumentRepositoryInterface,
            parser: ParserInterface,
            user_id: int,
            chunk_size: int = None,
            chunk_overlap: int = None,
            text_splitter = None,
    ):
        super().__init__(chunk_size, chunk_overlap, text_splitter)
        self.document_repo = document_repo
        self.parser = parser
        self.user_id = user_id


    @staticmethod
    def generate_name():
        return uuid4()

    def divide_into_chunks(self, pdf_model: PDFBase) -> list[ChunkBase]:
        return self._divide_into_chunks_by_user_id(pdf_model, self.user_id)
