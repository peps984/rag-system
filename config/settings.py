import os
from dotenv import load_dotenv

load_dotenv()

# app settings
APP_NAME = os.getenv("APP_NAME", "RAG System")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# db settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")