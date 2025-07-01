# Nail Image Embedder API

The **Nail Image Embedder API** is a FastAPI-based backend service for embedding nail design images and storing both **vector representations (Qdrant)** and **metadata (PostgreSQL)** for similarity-based search and management.

This API is intended to be **called by frontend clients or automated scrapers**, and **not directly used by end-users**.


## 🚀 Features

- Upload single or batch images with metadata to S3 bucket named imagemtadata2025
- Extract image embeddings using CLIP
- Store embeddings in Qdrant vector DB
- Store metadata in PostgreSQL (e.g., filename, style, tags)
- Search for similar images by image or text
- Delete image from both vector DB and metadata DB


## 🧱 Tech Stack

| Component     | Tech                     |
|---------------|--------------------------|
| API Framework | FastAPI                  |
| Embedding     | CLIP |
| Vector DB     | Qdrant                   |
| Metadata DB   | PostgreSQL               |
| Server        | uvicorn                  |
| Deployment    | Docker & Docker Compose  |



## 📁 Project Structure

```bash
nail-embedder/
├── app/
│   ├── config.py           # Environment settings
│   ├── db_postgres.py      # PostgreSQL handler
│   ├── db_qdrant.py        # Qdrant handler
│   ├── embedder.py         # Embedding logic
│   ├── processor.py        # Image processing and API logic
│   ├── s3_utils.py         # S3 upload and bucket management
│   └── main.py                 # FastAPI app entrypoint
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker Compose setup
├── .env                    # Environment variables (user-provided)
├── tests/                  # Test cases
```


## ⚙️ Local Setup

1. **Clone the repo**
```bash
git clone <your-repo-url>
cd nail-embedder
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Create a `.env` file** in the root directory with the following content:
```env
# PostgreSQL settings
POSTGRES_DB=<your_postgres_db_name>
POSTGRES_USER=<your_postgres_username>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_HOST=<your_postgres_host>
POSTGRES_PORT=<your_postgres_port>

# Qdrant settings
QDRANT_HOST=<your_qdrant_host>
QDRANT_PORT=<your_qdrant_port>
QDRANT_HTTPS=<true_or_false>
QDRANT_COLLECTION=<your_qdrant_collection_name>
VECTOR_SIZE=<your_vector_size>

# S3 settings
AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
AWS_S3_BUCKET=pretty-images
AWS_S3_REGION=us-west-1
```
4. **Start the API**
```bash
uvicorn app.main:app
# The S3 bucket will be auto-created if it does not exist
```
5. **Access the API** at `http://127.0.0.1:8000/docs`

---

## 🐳 Docker Deployment

To deploy using Docker, ensure you have Docker and Docker Compose installed, then run:

1. **Create a `.env` file** in the root directory (see above for variables).
2. **Run Docker Compose**
```bash
docker-compose up --build
```
- PostgreSQL will be available at `localhost:5432`
- Qdrant will be available at `localhost:6333`
- The API will be available at `http://localhost:8000/docs`

---

## 🔗 API Endpoints

| Method | Endpoint            | Description                                 |
|--------|---------------------|---------------------------------------------|
| POST   | `/upload`           | Upload and process a single image           |
| POST   | `/upload/batch`     | Upload and process multiple images (batch)  |
| DELETE | `/images/{image_id}`| Delete an image from both databases         |
| POST   | `/search/image`     | Search for similar images by uploading image|
| POST   | `/search/text`      | Search for similar images by text           |

### Example: Upload Single Image
- **POST** `/upload`
- Form-data: `file` (image), `metadata` (JSON string, optional)

### Example: Batch Upload
- **POST** `/upload/batch`
- Form-data: `files` (multiple images), `metadata_list` (JSON list, optional)

### Example: Search by Image
- **POST** `/search/image`
- Form-data: `file` (image), `limit` (optional)

### Example: Search by Text
- **POST** `/search/text`
- Form-data: `text` (string), `limit` (optional)

### Example: Delete Image
- **DELETE** `/images/{image_id}`


## 📌 TODOs / Improvements

1. Add authentication (JWT / API Key)
2. Add support for tagging and categories
3. Add batch delete support

## 📞 Contact

For any inquiries or support, please reach out to:

- **Name**: Sunny Lee
- **Email**: happysujnny649@gmail.com
