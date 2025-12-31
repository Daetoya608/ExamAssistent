import pytest
from pathlib import Path
import pymupdf
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_settings():
    """Подменяет реальные настройки на тестовые значения"""
    with patch("app.infrastructure.parsers.pdf_parser.pdf_parser.get_settings") as mocked:
        mock_config = MagicMock()
        mock_config.CHUNK_SIZE = 100
        mock_config.CHUNK_OVERLAP = 20
        mocked.return_value = mock_config
        yield mock_config


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Создает настоящий временный PDF-файл для тестов"""
    pdf_path = tmp_path / "test_exam.pdf"
    doc = pymupdf.open()

    # Страница 1
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Mathematical analysis. Lecture 1. Integrals.")

    # Страница 2
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Second page. Derivatives.")

    doc.save(pdf_path)
    doc.close()
    return pdf_path