from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # PostgreSQL settings
    POSTGRES_DB: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432

    # Qdrant settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "clip_embeddings"
    VECTOR_SIZE: int = 512
    QDRANT_API_KEY: str = ""   
    QDRANT_HTTPS: bool = False

    # CLIP model
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"

    # API server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # S3 settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "pretty-images"
    AWS_S3_REGION: str = "us-west-1" 
    

    class Config:
        env_file = ".env"

settings = Settings()