import hashlib

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
    return hashlib.sha256(text.strip().encode()).hexdigest()


def get_points_from_chunks(chunks: list[ChunkBase], encoder: SentenceTransformer) -> list[PointStruct]:
    points = [
        PointStruct(
            id=generate_id(chunk.content),
            vector=encoder.encode(chunk.content).tolist(),
            payload=chunk.model_dump(),
        )
        for chunk in chunks
    ]
    return points


def get_chunks_from_scored_points(scored_points: list[ScoredPoint]) -> list[ChunkBase]:
    chunks = [ChunkBase(**point.payload) for point in scored_points]
    return chunks


def get_encoder(encoder):
    if encoder is None:
        return SentenceTransformer('BAAI/bge-m3', device='cuda')
    return encoder
