import hashlib
import os
import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, ScoredPoint

from app.core.config.utils import get_settings
from app.domains.documents.schemas import ChunkBase


def get_qdrant_url(qdrant_url: str) -> str:
    if qdrant_url is None:
        settings = get_settings()
        qdrant_url = settings.qdrant_uri
    return qdrant_url


def generate_id(text: str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))


def get_points_from_chunks(chunks: list[ChunkBase], encoder: SentenceTransformer) -> list[PointStruct]:
    # 1. Собираем все тексты из чанков
    texts = [chunk.content for chunk in chunks]

    # 2. Векторизуем всё за один проход (SentenceTransformer сам эффективно разделит это на батчи)
    # Параметр batch_size здесь контролирует нагрузку на GPU/CPU
    embeddings = encoder.encode(texts, batch_size=32, show_progress_bar=True)

    # 3. Собираем список PointStruct, используя готовые векторы
    points = [
        PointStruct(
            id=generate_id(chunk.content),
            vector=embeddings[i].tolist(),
            payload=chunk.model_dump(),
        )
        for i, chunk in enumerate(chunks)
    ]

    return points


def get_chunks_from_scored_points(scored_points: list[ScoredPoint]) -> list[ChunkBase]:
    chunks = [ChunkBase(**point.payload) for point in scored_points]
    return chunks


def get_encoder(encoder):
    if encoder is None:
        # os.environ['TRANSFORMERS_OFFLINE'] = '1'
        # os.environ['HF_HUB_OFFLINE'] = '1'
        return SentenceTransformer(
            "/home/daetoya/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181",
            # local_files_only=True,
            device='cuda'
        )
    return encoder


def get_collection_name(collection_name: str = None):
    if collection_name is None:
        settings = get_settings()
        return settings.B2_DEFAULT_COLLECTION_NAME
    return collection_name
