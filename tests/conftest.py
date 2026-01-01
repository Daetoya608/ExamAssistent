import pytest
from pathlib import Path
import pymupdf
from unittest.mock import patch, MagicMock

from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository


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


@pytest.fixture
def mock_encoder():
    # ПУТЬ: убедитесь, что здесь docs_repository
    with patch('app.infrastructure.vector_db.qdrant.docs_repository.SentenceTransformer') as mock:
        instance = mock.return_value
        instance.get_sentence_embedding_dimension.return_value = 1024
        mock_vector = MagicMock()
        mock_vector.tolist.return_value = [0.1] * 1024
        instance.encode.return_value = mock_vector
        yield instance

@pytest.fixture
def repo(mock_encoder):
    # Патчим QdrantClient, чтобы он не лез в сеть
    with patch('app.infrastructure.vector_db.qdrant.docs_repository.QdrantClient') as mock_client:
        from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
        repository = QdrantFilesRepository(
            collection_name="test_collection",
            qdrant_url="http://localhost:6333"
        )
        # Явно делаем клиент моком, чтобы работал .return_value
        repository.client = MagicMock()
        yield repository