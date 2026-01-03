import pytest
from unittest.mock import MagicMock, patch
from qdrant_client import models
from app.infrastructure.vector_db.qdrant.docs_repository import QdrantFilesRepository
from app.domains.documents.schemas import ChunkBase


def test_generate_id_consistency():
    """Проверяем, что хеш всегда одинаковый для одного текста"""
    from app.infrastructure.vector_db.qdrant.utils import generate_id
    text = "  Sample text  "
    id1 = generate_id(text)
    id2 = generate_id("Sample text")
    assert id1 == id2
    assert len(id1) == 64  # Длина SHA-256 в hex


def test_get_points_from_chunks(mock_encoder):
    from app.infrastructure.vector_db.qdrant.utils import get_points_from_chunks

    chunks = [
        ChunkBase(
            content="Text 1",
            file_id="f1",
            source="test.pdf",
            page_num=1,
            chunk_index=0
        )
    ]

    points = get_points_from_chunks(chunks, mock_encoder)
    assert len(points) == 1
    assert points[0].payload["source"] == "test.pdf"


def test_upload_points_execution(repo, mock_encoder):
    chunks = [
        ChunkBase(
            content="data",
            file_id="1",
            source="file.pdf",
            page_num=1,
            chunk_index=0
        )
    ]
    repo.upload_points(chunks)
    assert repo.client.upload_points.called


def test_get_chunks_from_scored_points():
    from app.infrastructure.vector_db.qdrant.utils import get_chunks_from_scored_points

    mock_scored_points = [
        models.ScoredPoint(
            id=1,
            version=1,
            score=0.99,
            payload={
                "content": "Found text",
                "file_id": "file_abc",
                "source": "manual.pdf",
                "page_num": 10,
                "chunk_index": 5
            }
        )
    ]

    chunks = get_chunks_from_scored_points(mock_scored_points)
    assert chunks[0].page_num == 10


@patch('app.infrastructure.vector_db.qdrant.docs_repository.get_chunks_from_scored_points')
def test_search_calls_proper_methods(mock_get_chunks, repo):
    """Проверяем всю цепочку поиска"""
    mock_get_chunks.return_value = [
        ChunkBase(
            content="res",
            file_id="1",
            source="test.pdf",
            page_num=1,
            chunk_index=0
        )
    ]

    # Мокаем результат query_points
    mock_query_res = MagicMock()
    mock_query_res.points = []
    repo.client.query_points.return_value = mock_query_res

    repo.search("test query", file_id="spec_file")

    # Проверяем, что энкодер был вызван
    repo.encoder.encode.assert_called_with("test query")

    # Проверяем фильтрацию
    query_args = repo.client.query_points.call_args[1]
    assert query_args['query_filter'].must[0].match.value == "spec_file"


def test_init_storage_creates_collection(repo):
    """Проверяем, что инициализация создает коллекцию с верными параметрами"""
    repo.init_storage()

    repo.client.create_collection.assert_called_once()
    _, kwargs = repo.client.create_collection.call_args
    assert kwargs['collection_name'] == "test_collection"
    assert kwargs['vectors_config'].size == 1024
    assert kwargs['vectors_config'].distance == models.Distance.COSINE


def test_upload_points_uses_correct_params(repo):
    """Проверяем, что параметры параллельности и ретраев прокидываются в клиент"""
    # Создаем мок клиента, чтобы не было ConnectError
    repo.client.upload_points = MagicMock()

    chunks = [
        ChunkBase(
            content="test text",
            file_id="file_1",
            source="manual.pdf",
            page_num=1,
            chunk_index=1
        )
    ]

    repo.upload_points(chunks)

    repo.client.upload_points.assert_called_once()
    _, kwargs = repo.client.upload_points.call_args
    assert kwargs['parallel'] == repo.parallel_count
    assert kwargs['max_retries'] == repo.max_retries


def test_search_empty_query_returns_nothing(repo):
    """Проверяем, что пустой запрос не идет в базу и модель"""
    results = repo.search(query_text="  ")
    assert results == []
    repo.encoder.encode.assert_not_called()


def test_search_with_file_filter(repo):
    """Теперь repo.client — это MagicMock, ошибка с return_value уйдет"""
    mock_response = MagicMock()
    mock_response.points = []
    repo.client.query_points.return_value = mock_response

    repo.search(query_text="test", file_id="doc_123")
    repo.client.query_points.assert_called_once()


def test_generate_id_is_deterministic():
    """Проверяем, что один и тот же текст всегда дает одинаковый ID (дедупликация)"""
    from app.infrastructure.vector_db.qdrant.utils import generate_id
    text = "Контент для хеширования"
    id1 = generate_id(text)
    id2 = generate_id(text)
    assert id1 == id2
    assert isinstance(id1, str)