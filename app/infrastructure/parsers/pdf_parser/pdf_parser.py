from pathlib import Path

import pymupdf
from pydantic import ValidationError
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domains.documents.schemas import PDFBase, ChunkBase
from app.core.config.utils import get_settings


class ParserPDF:
    def __init__(self, pdf_file_path: Path):
        self.pdf_model = self._convert_pdf_to_model(pdf_file_path)
        settings = get_settings()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP


    def _create_model_from_dict(self, documents_data: dict) -> PDFBase:
        try:
            page_model = PDFBase.model_validate(documents_data)
            return page_model
        except ValidationError as e:
            # Здесь мы точно знаем, что проблема в структуре данных
            print(f"Данные страницы не соответствуют схеме: {e.json()}")
        except Exception as e:
            # Здесь ловим всё остальное (непредвиденные ошибки)
            print(f"Неизвестная ошибка: {e}")
        return PDFBase()


    def _convert_pdf_to_model(self, pdf_file_path: Path) -> PDFBase:
        documents_data = {"pages": []}
        with pymupdf.open(pdf_file_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                # 1. Извлекаем текст как строку (без лишнего encode)
                text = page.get_text()

                # 2. Очищаем от лишних пробелов по краям
                clean_text = text.strip()

                if not clean_text:
                    continue

                # 3. Сохраняем текст вместе с метаданными
                documents_data["pages"].append({
                    "content": clean_text,
                    "metadata": {
                        "source": pdf_file_path.name,
                        "page": page_num,
                    }
                })

        return self._create_model_from_dict(documents_data)


    def _divide_page_into_chunks(self, text_splitter: RecursiveCharacterTextSplitter, page_index) -> list[ChunkBase]:
        chunks = list()
        texts = text_splitter.split_text(self.pdf_model.pages[page_index].content)
        for chunk_index, chunk_text in enumerate(texts):
            chunk_model = ChunkBase(
                content=chunk_text,
                file_id=None,
                source=self.pdf_model.pages[page_index].metadata.source,
                page_num=self.pdf_model.pages[page_index].metadata.page,
                chunk_index=chunk_index,
            )
            chunks.append(chunk_model)
        return chunks


    def divide_into_chunks(self, chunk_size: int = None, chunk_overlap: int = None) -> list[ChunkBase]:
        if chunk_size is None: chunk_size = self.chunk_size
        if chunk_overlap is None: chunk_overlap = self.chunk_overlap

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = []
        for page_index in range(len(self.pdf_model.pages)):
            page_chunks = self._divide_page_into_chunks(text_splitter, page_index)
            chunks.extend(page_chunks)

        return chunks
