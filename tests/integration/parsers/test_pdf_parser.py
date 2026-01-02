import pytest
import io
import fitz  # PyMuPDF
from unittest.mock import MagicMock
from pydantic import ValidationError

from app.domains.documents.schemas import PDFBase, PDFPage
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF

@pytest.fixture
def create_pdf_bytes():
    """Фикстура для создания реального PDF в памяти."""

    def _create(pages_content: list[str], filename="test.pdf"):
        doc = fitz.open()
        for text in pages_content:
            page = doc.new_page()
            # Вставляем текст в координаты (50, 50)
            page.insert_text((50, 50), text)

        pdf_bytes = io.BytesIO(doc.tobytes())
        # Добавляем атрибут name, так как ParserPDF его ожидает
        pdf_bytes.name = filename
        doc.close()
        return pdf_bytes

    return _create


class TestParserPDF:

    def test_successful_parsing(self, create_pdf_bytes):
        """Теперь передаем имя файла явно, и тест должен пройти."""
        content = ["Page 1 text"]
        pdf_io = create_pdf_bytes(content)

        # Передаем имя файла вторым аргументом
        parser = ParserPDF(pdf_io, filename="manual.pdf")
        result = parser.get_pdf()

        assert len(result.pages) == 1
        assert result.pages[0].metadata.source == "manual.pdf"
        assert result.pages[0].content == "Page 1 text"

    def test_invalid_pdf_data(self):
        """
        Проверяем, как парсер реагирует на 'битые' данные.
        Вместо AttributeError теперь ожидаем пустую модель,
        так как мы добавили try-except вокруг pymupdf.open.
        """
        bad_pdf_io = io.BytesIO(b"not a pdf content")

        parser = ParserPDF(bad_pdf_io, filename="corrupt.pdf")
        result = parser.get_pdf()

        # Парсер должен поймать ошибку и вернуть объект с пустым списком страниц
        assert isinstance(result, PDFBase)
        assert len(result.pages) == 0

    def test_empty_page_exclusion(self, create_pdf_bytes):
        """Проверка, что пустые страницы игнорируются (как в коде)."""
        # Одна страница с текстом, вторая пустая
        content = ["Valid text", "   "]
        pdf_io = create_pdf_bytes(content)

        parser = ParserPDF(pdf_io)
        result = parser.get_pdf()

        assert len(result.pages) == 1
        assert result.pages[0].content == "Valid text"

    def test_empty_pdf_logic(self, create_pdf_bytes):
        """Проверка фильтрации пустых страниц."""
        pdf_io = create_pdf_bytes(["", "  ", "\n"])  # Три пустых страницы

        parser = ParserPDF(pdf_io)
        result = parser.get_pdf()

        assert len(result.pages) == 0

    def test_create_model_from_dict_validation_error(self, monkeypatch):
        """Проверка обработки ошибок валидации Pydantic."""
        # Создаем минимальный PDF для инициализации
        doc = fitz.open()
        doc.new_page()
        pdf_io = io.BytesIO(doc.tobytes())
        pdf_io.name = "error.pdf"

        # Имитируем некорректные данные (например, page = -1 при gt=0)
        bad_data = {
            "pages": [{
                "content": "test",
                "metadata": {"source": "test.pdf", "page": -1}
            }]
        }

        parser = ParserPDF(pdf_io)
        # Вызываем внутренний метод с плохими данными
        result = parser._create_model_from_dict(bad_data)

        # Согласно вашему коду, при ошибке возвращается пустой PDFBase
        assert isinstance(result, PDFBase)
        assert len(result.pages) == 0

    def test_get_pdf_returns_model(self, create_pdf_bytes):
        """Проверка, что get_pdf возвращает сохраненную модель."""
        pdf_io = create_pdf_bytes(["Hello"])
        parser = ParserPDF(pdf_io)

        model = parser.get_pdf()
        assert model == parser.pdf_model
