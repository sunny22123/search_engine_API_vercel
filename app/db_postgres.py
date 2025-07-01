import psycopg2
from psycopg2.extras import DictCursor, Json
from .config import settings

class PostgresDB:
    def __init__(self):
        self.conn_params = {
            'dbname': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'host': settings.POSTGRES_HOST,
            'port': settings.POSTGRES_PORT
        }
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables if they don't exist."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pretty_images_metadata (
                        uuid UUID PRIMARY KEY,
                        filename TEXT NOT NULL,
                        upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    )
                """)
                conn.commit()

    def get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(**self.conn_params)

    def insert_image_metadata(self, image_uuid: str, filename: str, metadata: dict = None):
        """Insert image metadata into the database."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pretty_images_metadata (uuid, filename, metadata)
                    VALUES (%s, %s, %s)
                    """,
                    (image_uuid, filename, Json(metadata) if metadata is not None else None)
                )
                conn.commit()

    def get_image_metadata(self, image_uuid: str) -> dict:
        """Retrieve image metadata by UUID."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM pretty_images_metadata WHERE uuid = %s
                    """,
                    (image_uuid,)
                )
                result = cur.fetchone()
                return dict(result) if result else None

    def delete_image_metadata(self, image_uuid: str):
        """Delete image metadata by UUID."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM pretty_images_metadata WHERE uuid = %s
                    """,
                    (image_uuid,)
                )
                conn.commit()

    def image_exists(self, image_uuid: str) -> bool:
        """Check if an image exists in the database by UUID."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pretty_images_metadata WHERE uuid = %s LIMIT 1",
                    (image_uuid,)
                )
                return cur.fetchone() is not None

postgres_db = PostgresDB() 