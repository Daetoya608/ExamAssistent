from typing import List, Any, Optional

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.domains.documents.schemas import ChunkBase
from app.domains.vector_db.vector_db_interface import VectorDBInterface
from app.infrastructure.vector_db.qdrant.utils import (get_qdrant_url, get_points_from_chunks,
                                                       get_chunks_from_scored_points, get_encoder,
                                                       get_collection_name)


class QdrantFilesRepository(VectorDBInterface):
    def __init__(
            self,
            collection_name: str = None,
            qdrant_url = None,
            parallel_count: int = 4,
            max_retries: int = 3,
            encoder = None,
    ):
        self.collection_name = get_collection_name(collection_name)
        self.client = QdrantClient(url=get_qdrant_url(qdrant_url))
        self.encoder = get_encoder(encoder)
        self.parallel_count = parallel_count
        self.max_retries = max_retries


    def init_storage(self) -> None:
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE,
            ),
        )


    def upload_points(self, chunks: list[ChunkBase]) -> None:
        points = get_points_from_chunks(chunks, self.encoder)
        self.client.upload_points(
            collection_name=self.collection_name,
            points=points,
            parallel=self.parallel_count,
            max_retries=self.max_retries,
        )


    def upsert_batches(self, chunks: List[ChunkBase]) -> None:
        # points = get_points_from_chunks(chunks, self.encoder)
        # self.client.upsert(
        #     collection_name=self.collection_name,
        #     points=points,
        # )
        points = get_points_from_chunks(chunks, self.encoder)
        self.client.upload_points(
            collection_name=self.collection_name,
            points=points,
            parallel=self.parallel_count,
            max_retries=self.max_retries,
        )


    def search(
            self,
            query_text: str,
            top_k: int = 5,
            file_id: Optional[str] = None
    ) -> List[ChunkBase]:
        if not query_text or not query_text.strip():
            return []
        query_filter = None if file_id is None else models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id",
                        match=models.MatchValue(value=file_id)
                    )
                ]
            )
        found_points = self.client.query_points(
            collection_name=self.collection_name,
            query = self.encoder.encode(query_text).tolist(),
            query_filter=query_filter,
            limit=top_k,
        ).points
        return get_chunks_from_scored_points(found_points)


    def delete_by_file_id(self, file_id: str) -> None:
        pass


    def get_all_files(self) -> List[str]:
        pass
