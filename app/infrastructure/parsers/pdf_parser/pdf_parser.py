from pathlib import Path
import io

import pymupdf
from pydantic import ValidationError

from app.domains.documents.schemas import PDFBase
from app.domains.documents.parser_interface import ParserInterface


class ParserPDF(ParserInterface):
    def _create_model_from_dict(self, documents_data: dict) -> PDFBase:
        try:
            return PDFBase.model_validate(documents_data)
        except ValidationError as e:
            print(f"Данные страницы не соответствуют схеме: {e.json()}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
        return PDFBase()

    def _convert_pdf_to_model(self, file_bytes: io.BytesIO, filename: str) -> PDFBase:
        documents_data = {"pages": []}

        # 1. Проверяем входные данные
        try:
            raw_data = file_bytes.getvalue()
            if len(raw_data) == 0:
                return PDFBase()
        except Exception as e:
            return PDFBase()

        try:
            # 2. Пытаемся открыть PDF
            with pymupdf.open(stream=raw_data, filetype="pdf") as doc:

                # 3. Цикл по страницам
                for page_num, page in enumerate(doc, start=1):
                    try:
                        text = page.get_text()
                        clean_text = text.strip()

                        if not clean_text:
                            continue

                        documents_data["pages"].append({
                            "content": clean_text,
                            "metadata": {
                                "source": filename,
                                "page": page_num,
                            }
                        })
                    except Exception as page_err:
                        print(f"[DEBUG] ОШИБКА на странице {page_num}: {page_err}")

            # 4. Финальная проверка данных перед созданием модели
            # Предполагаем, что у вас есть этот метод (как в предыдущих сообщениях)
            result = self._create_model_from_dict(documents_data)
            return result

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return PDFBase()

    def get_pdf(self, file_bytes: io.BytesIO, filename: str = "unknown") -> PDFBase:
        return self._convert_pdf_to_model(file_bytes, filename)
