import pytest
from app.infrastructure.parsers.pdf_parser.pdf_parser import ParserPDF
from app.domains.documents.schemas import PDFBase, ChunkBase


def test_parser_initialization_and_conversion(temp_pdf_file, mock_settings):
    """Проверяем, что при создании объекта файл читается и конвертируется в PDFBase"""
    parser = ParserPDF(temp_pdf_file)

    assert isinstance(parser.pdf_model, PDFBase)
    assert len(parser.pdf_model.pages) == 2
    assert "Integrals" in parser.pdf_model.pages[0].content
    # Здесь всё верно: у страницы есть поле metadata
    assert parser.pdf_model.pages[0].metadata.page == 1


def test_divide_into_chunks_logic(temp_pdf_file, mock_settings):
    """Проверяем, что метод divide_into_chunks возвращает список чанков"""
    parser = ParserPDF(temp_pdf_file)

    chunks = parser.divide_into_chunks()

    assert isinstance(chunks, list)
    assert len(chunks) >= 2
    assert isinstance(chunks[0], ChunkBase)

    # ИСПРАВЛЕНО: Обращаемся к полям напрямую, так как ChunkBase наследует ChunkMetadata
    assert chunks[0].source == "test_exam.pdf"
    assert chunks[0].page_num == 1
    assert chunks[0].chunk_index == 0


def test_custom_chunk_params(temp_pdf_file, mock_settings):
    """Проверяем кастомные параметры разбиения"""
    parser = ParserPDF(temp_pdf_file)

    # Параметры должны ограничить длину контента
    chunks = parser.divide_into_chunks(chunk_size=10, chunk_overlap=0)

    assert len(chunks) > 0
    assert len(chunks[0].content) <= 10


def test_error_handling_invalid_dict(temp_pdf_file, mock_settings):
    """Проверяем обработку некорректного словаря при создании модели"""
    parser = ParserPDF(temp_pdf_file)

    bad_data = {"pages": "не список"}
    result = parser._create_model_from_dict(bad_data)

    assert isinstance(result, PDFBase)
    assert len(result.pages) == 0