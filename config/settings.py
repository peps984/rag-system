import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# app settings
APP_NAME = os.getenv("APP_NAME", "RAG System")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# db settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")

# file upload settings
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,txt,md").split(",")

UPLOAD_DIR.mkdir(exist_ok=True)

# chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set!")