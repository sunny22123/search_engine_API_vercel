from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, PointIdsList
import numpy as np
from .config import settings

class QdrantDB:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection only if it does not exist."""
        existing = self.client.get_collections().collections
        if settings.QDRANT_COLLECTION not in [c.name for c in existing]:
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=settings.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )

    def insert_vector(self, image_id: str, vector: np.ndarray, metadata: dict = None):
        """Insert a vector and optional metadata into Qdrant."""
        point = PointStruct(
            id=image_id,
            vector=vector.tolist(),
            payload=metadata or {}
        )
        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[point]
        )

    def search_similar(self, query_vector: np.ndarray, limit: int = 10):
        """Return top-k similar vectors."""
        return self.client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector.tolist(),
            limit=limit
        )

    def delete_vector(self, image_id: str):
        """Delete a vector by ID."""
        self.client.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=PointIdsList(points=[image_id])
        )
    # search by id after user click the image
    def search_similar_by_id(self, image_id: str, limit: int = 10):
        point = self.client.retrieve(
            collection_name=settings.QDRANT_COLLECTION,
            ids=[image_id]
        )
        if not point or not hasattr(point[0], 'vectors'):
            raise ValueError(f"can't find id={image_id} vectors, please check Qdrant data!")
        vectors = point[0].vectors
        # return 'default' vectors
        if isinstance(vectors, dict):
            embedding = vectors.get('default') or list(vectors.values())[0]
        else:
            embedding = vectors
        if embedding is None:
            raise ValueError(f"can't find id={image_id} embedding, please check Qdrant data!")
        return self.search_similar(embedding, limit=limit)

# Create singleton instance
qdrant_db = QdrantDB()
