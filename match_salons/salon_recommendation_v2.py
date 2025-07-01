from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Qdrant client
qdrant_client = QdrantClient(host="localhost", port=6333)

print("DB:", os.getenv("POSTGRES_DB"))
print("USER:", os.getenv("POSTGRES_USER"))
print("HOST:", os.getenv("POSTGRES_HOST"))
print("PORT:", os.getenv("POSTGRES_PORT"))

# Database connection 
def get_pg_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

class SalonResult(BaseModel):
    salon_id: str
    business_name: str
    address: str
    overall_price_level: str
    review_total: Optional[int]
    average_rating: Optional[float]
    features: Optional[str]
    image_id: str
    similarity: float

@router.get("/api/salon-recommendation-v2", response_model=List[SalonResult])
async def recommend_salon_by_image_id(image_id: str = Query(...), top_k: int = 4):
    # 1. get embedding from pretty_images_clip
    point = qdrant_client.retrieve(
        collection_name="pretty_images_clip",
        ids=[image_id],
        with_vectors=True
    )
    if not point or point[0].vector is None:
        raise HTTPException(status_code=404, detail="Image embedding not found in pretty_images_clip")
    embedding = point[0].vector

    # 2. use this embedding to find similar images in salon_images_clip
    hits = qdrant_client.search(
        collection_name="salon_images_clip",
        query_vector=embedding,
        limit=top_k
    )
    image_ids = [hit.id for hit in hits]
    similarities = [hit.score for hit in hits]
    print(f"[DEBUG] Qdrant hits image_ids: {image_ids}")
    print(f"[DEBUG] Qdrant similarities: {similarities}")


    results = []
    # 3. find PostgreSQL
    conn = get_pg_conn()
    with conn.cursor() as cur:
        for img_id, similarity in zip(image_ids, similarities):
            # find salon_id
            cur.execute("SELECT salon_id FROM salon_images WHERE image_id = %s", (img_id,))
            row = cur.fetchone()
            print(f"[DEBUG] find salon_images image_id={img_id} result: {row}")
            if not row:
                continue
            salon_id = row[0]
            # remove dash from salon_id
            salon_id_no_dash = salon_id.replace("-", "") if isinstance(salon_id, str) else salon_id
            # find salon info
            cur.execute("""
                SELECT salon_id, business_name, address, overall_price_level, review_total, average_rating, amenities
                FROM salons WHERE REPLACE(salon_id, '-', '') = %s
            """, (salon_id_no_dash,))
            salon = cur.fetchone()
            print(f"[DEBUG] find salons salon_id={salon_id} result: {salon}")
            if not salon:
                continue
            results.append(SalonResult(
                salon_id=salon[0],
                business_name=salon[1],
                address=salon[2],
                overall_price_level=salon[3],
                review_total=salon[4],
                average_rating=salon[5],
                features=salon[6],  
                image_id=img_id,
                similarity=similarity
            ))
    conn.close()
    return results