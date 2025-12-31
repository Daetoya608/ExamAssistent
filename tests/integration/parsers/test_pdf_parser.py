import pytest
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF
from app.infrastructure.parsers.pdf_parser.schemas import PDFBase, ChunkBase


def test_parser_initialization_and_conversion(temp_pdf_file, mock_settings):
    """Проверяем, что при создании объекта файл читается и конвертируется в PDFBase"""
    parser = ParserPDF(temp_pdf_file)

    # Проверяем, что создалась модель с 2 страницами
    assert isinstance(parser.pdf_model, PDFBase)
    assert len(parser.pdf_model.pages) == 2
    assert "Integrals" in parser.pdf_model.pages[0].content
    assert parser.pdf_model.pages[0].metadata.page == 1


def test_divide_into_chunks_logic(temp_pdf_file, mock_settings):
    """Проверяем, что метод divide_into_chunks возвращает список чанков с метаданными"""
    parser = ParserPDF(temp_pdf_file)

    # Вызываем разбиение (параметры возьмутся из mock_settings)
    chunks = parser.divide_into_chunks()

    assert isinstance(chunks, list)
    assert len(chunks) >= 2
    assert isinstance(chunks[0], ChunkBase)

    # Проверяем, что в метаданных чанка есть нужная информация
    assert chunks[0].metadata.source == "test_exam.pdf"
    assert chunks[0].metadata.page_num == 1
    assert chunks[0].metadata.chunk_index == 0


def test_custom_chunk_params(temp_pdf_file, mock_settings):
    """Проверяем, что ручные параметры в методе перекрывают дефолтные"""
    parser = ParserPDF(temp_pdf_file)

    # Делаем очень маленький размер чанка (5 символов)
    # Это должно создать много мелких чанков
    chunks = parser.divide_into_chunks(chunk_size=10, chunk_overlap=0)

    assert len(chunks) > 0
    assert len(chunks[0].content) <= 10


def test_error_handling_invalid_dict(temp_pdf_file, mock_settings):
    """Проверяем, что при кривых данных возвращается пустой PDFBase (твой try-except)"""
    parser = ParserPDF(temp_pdf_file)

    # Имитируем ошибку валидации
    bad_data = {"pages": "это не список, это строка"}
    result = parser._create_model_from_dict(bad_data)

    assert isinstance(result, PDFBase)
    assert len(result.pages) == 0