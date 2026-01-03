import pytest
import io
import fitz  # PyMuPDF
from app.domains.documents.schemas import PDFBase
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF


@pytest.fixture
def create_pdf_bytes():
    """Фикстура для создания реального PDF в памяти."""

    def _create(pages_content: list[str]):
        doc = fitz.open()
        for text in pages_content:
            page = doc.new_page()
            page.insert_text((50, 50), text)

        pdf_bytes = io.BytesIO(doc.tobytes())
        doc.close()
        return pdf_bytes

    return _create


class TestParserPDF:

    def test_successful_parsing(self, create_pdf_bytes):
        """Проверка успешного парсинга.
        Примечание: так как get_pdf не принимает имя, ждем 'unknown'
        """
        content = ["Page 1 text"]
        pdf_io = create_pdf_bytes(content)
        parser = ParserPDF()

        # Вызываем метод, передавая байты
        result = parser.get_pdf(pdf_io)

        assert len(result.pages) == 1
        assert result.pages[0].content == "Page 1 text"
        # В текущей реализации get_pdf не прокидывает имя, будет unknown
        assert result.pages[0].metadata.source == "unknown"

    def test_invalid_pdf_data(self):
        """Проверка реакции на некорректные данные (не PDF)."""
        bad_pdf_io = io.BytesIO(b"not a pdf content")
        parser = ParserPDF()

        result = parser.get_pdf(bad_pdf_io)

        # Ожидаем пустую модель PDFBase согласно блоку except в коде
        assert isinstance(result, PDFBase)
        assert len(result.pages) == 0

    def test_empty_page_exclusion(self, create_pdf_bytes):
        """Проверка, что пустые страницы (или только с пробелами) игнорируются."""
        content = ["Valid text", "   ", "\n"]
        pdf_io = create_pdf_bytes(content)
        parser = ParserPDF()

        result = parser.get_pdf(pdf_io)

        # Должна остаться только одна страница
        assert len(result.pages) == 1
        assert result.pages[0].content == "Valid text"

    def test_create_model_from_dict_validation_error(self):
        """Проверка обработки ошибок валидации Pydantic."""
        parser = ParserPDF()

        # Данные, которые не пройдут валидацию (например, вместо списка страниц — строка)
        bad_data = {"pages": "not a list"}

        result = parser._create_model_from_dict(bad_data)

        # Должен вернуться пустой PDFBase
        assert isinstance(result, PDFBase)
        assert len(result.pages) == 0

    def test_metadata_page_numbering(self, create_pdf_bytes):
        """Проверка корректности нумерации страниц в метаданных."""
        content = ["Text 1", "Text 2"]
        pdf_io = create_pdf_bytes(content)
        parser = ParserPDF()

        result = parser.get_pdf(pdf_io)

        assert len(result.pages) == 2
        assert result.pages[0].metadata.page == 1
        assert result.pages[1].metadata.page == 2