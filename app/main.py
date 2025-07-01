from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import json
from app.db_qdrant import qdrant_db  
from app.processor import image_processor
from app.config import settings
from match_salons.salon_recommendation_v2 import router as salon_recommendation_router

app = FastAPI(title="Nail Image Embedder API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the salon recommendation router with /api prefix
app.include_router(salon_recommendation_router, prefix="/api")

@app.post("/api/search/image")
async def search_image(
    file: UploadFile = File(...),
    limit: int = 18
):
    """Search for similar images by uploading an image."""
    try:
        image_data = await file.read()
        results = image_processor.search_similar(image_data=image_data, limit=limit)
        return {"results": [{"id": r["id"], "score": r["score"]} for r in results]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/search/text")
async def search_text(
    text: str = Form(...),
    limit: int = 18
):
    """Search for similar images by text."""
    try:
        results = image_processor.search_similar_by_text(text=text, limit=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/api/images/{image_id}")
async def get_image_metadata(image_id: str):
    try:
        metadata = image_processor.get_metadata_by_id(image_id)
        if not metadata:
            raise HTTPException(
                status_code=404, 
                detail=f"Image with ID {image_id} not found"
            )
        return metadata
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving metadata: {str(e)}"
        )