from pathlib import Path
import io

import pymupdf
from pydantic import ValidationError

from app.domains.documents.schemas import PDFBase


class ParserPDF:

    def __init__(self, file_bytes: io.BytesIO, filename: str = "unknown"):
        self.filename = filename
        self.pdf_model = self._convert_pdf_to_model(file_bytes)


    def _create_model_from_dict(self, documents_data: dict) -> PDFBase:
        try:
            return PDFBase.model_validate(documents_data)
        except ValidationError as e:
            print(f"Данные страницы не соответствуют схеме: {e.json()}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
        return PDFBase()


    def _convert_pdf_to_model(self, file_bytes: io.BytesIO) -> PDFBase:
        documents_data = {"pages": []}

        try:
            with pymupdf.open(stream=file_bytes.getvalue(), filetype="pdf") as doc:
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text()
                    clean_text = text.strip()

                    if not clean_text:
                        continue

                    documents_data["pages"].append({
                        "content": clean_text,
                        "metadata": {
                            "source": self.filename,
                            "page": page_num,
                        }
                    })
        except Exception as e:
            print(f"Ошибка при парсинге PDF ({self.filename}): {e}")
            return PDFBase()

        return self._create_model_from_dict(documents_data)


    def get_pdf(self) -> PDFBase:
        return self.pdf_model
