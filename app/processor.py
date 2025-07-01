import uuid
from PIL import Image
from typing import Optional, List, Dict
import io

from .embedder import clip_embedder
from .db_postgres import postgres_db
from .db_qdrant import qdrant_db
from .s3_utils import upload_image_to_s3

class ImageProcessor:
    @staticmethod
    def process_image(
        image_data: bytes,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Process a single image: generate embedding and store in databases.
        
        Args:
            image_data (bytes): Raw image data
            filename (str): Original filename
            metadata (dict, optional): Additional metadata
            
        Returns:
            str: Generated UUID for the image
        """
        # Generate UUID
        image_id = str(uuid.uuid4())
        
        # Load and process image
        image = Image.open(io.BytesIO(image_data))
        
        # Generate embedding
        embedding = clip_embedder.get_image_embedding(image)
        
        # Upload image to S3 and add S3 URL to metadata
        s3_url = upload_image_to_s3(image_data, image_id)
        if metadata is None:
            metadata = {}
        metadata['s3_url'] = s3_url
        
        # Store metadata in PostgreSQL
        postgres_db.insert_image_metadata(
            image_id=image_id,
            filename=filename,
            metadata=metadata
        )
        
        # Store embedding in Qdrant
        qdrant_db.insert_vector(
            image_id=image_id,
            vector=embedding,
            metadata=metadata
        )
        
        return image_id

    @staticmethod
    def process_batch(
        image_data_list: List[bytes],
        filenames: List[str],
        metadata_list: Optional[List[Dict]] = None
    ) -> List[str]:
        """
        Process multiple images in batch.
        
        Args:
            image_data_list (list[bytes]): List of raw image data
            filenames (list[str]): List of original filenames
            metadata_list (list[dict], optional): List of metadata for each image
            
        Returns:
            list[str]: List of generated UUIDs
        """
        if metadata_list is None:
            metadata_list = [None] * len(image_data_list)
            
        # Generate UUIDs
        image_ids = [str(uuid.uuid4()) for _ in range(len(image_data_list))]
        
        # Load and process images
        images = [Image.open(io.BytesIO(data)) for data in image_data_list]
        
        # Generate embeddings
        embeddings = clip_embedder.get_batch_embeddings(images)
        
        # Store metadata in PostgreSQL
        for image_id, filename, metadata in zip(image_ids, filenames, metadata_list):
            postgres_db.insert_image_metadata(
                image_id=image_id,
                filename=filename,
                metadata=metadata
            )
        
        # Store embeddings in Qdrant
        for image_id, embedding, metadata in zip(image_ids, embeddings, metadata_list):
            qdrant_db.insert_vector(
                image_id=image_id,
                vector=embedding,
                metadata=metadata
            )
        
        return image_ids

    @staticmethod
    def search_similar(image_data: bytes, limit: int = 8) -> List[Dict]:
        """
        Search for similar images using a query image.
        
        Args:
            image_data (bytes): Raw image data of the query image
            limit (int): Maximum number of results to return
            
        Returns:
            list[dict]: List of similar images with their metadata
        """
        # Load and process query image
        query_image = Image.open(io.BytesIO(image_data))
        query_embedding = clip_embedder.get_image_embedding(query_image)
        
        # Search in Qdrant
        print("search_similar: query_vector shape", len(query_embedding))
        similar_vectors = qdrant_db.search_similar(query_embedding, limit=limit)
        print("Qdrant raw result:", similar_vectors)
        
        # Get metadata from PostgreSQL
        results = []
        for match in similar_vectors:
            metadata = postgres_db.get_image_metadata(match.id)
            if metadata:
                results.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': metadata
                })
        
        return results

    @staticmethod
    def delete_image(image_id: str):
        """
        Delete an image from both databases.
        
        Args:
            image_id (str): UUID of the image to delete
        """
        postgres_db.delete_image_metadata(image_id)
        qdrant_db.delete_vector(image_id)

    @staticmethod
    def search_similar_by_text(text: str, limit: int = 18) -> List[Dict]:
        """
        Search for similar images using a query text.
        Args:
            text (str): Query text
            limit (int): Maximum number of results to return
        Returns:
            list[dict]: List of similar images with their id and score
        """
        # Generate text embedding
        query_embedding = clip_embedder.get_text_embedding(text)
        print("text embedding:", query_embedding)
        # Qdrant search
        similar_vectors = qdrant_db.search_similar(query_embedding, limit=limit)
        print("Qdrant search result:", similar_vectors)
        # Only return id and score
        results = []
        for match in similar_vectors:
            results.append({
                'id': match.id,
                'score': match.score
            })
        return results
    
    

    @staticmethod
    def search_similar_by_id(image_id: str, limit: int = 18) -> List[Dict]:
        """
        Search for similar images using an existing image's id (embedding).
        """
        similar_vectors = qdrant_db.search_similar_by_id(image_id, limit=limit)
        results = []
        for match in similar_vectors:
            metadata = postgres_db.get_image_metadata(match.id)
            if metadata:
                results.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': metadata
                })
        return results

    @staticmethod
    def get_metadata_by_id(image_id: str) -> Dict:
        """
        Get metadata for an image by its ID.
        
        Args:
            image_id (str): UUID of the image
            
        Returns:
            dict: Image metadata or None if not found
        """
        return postgres_db.get_image_metadata(image_id)

image_processor = ImageProcessor() 