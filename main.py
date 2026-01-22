from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes import router
from config.settings import APP_NAME, APP_VERSION
from database.database import engine, Base
from database.models import Note
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
    print("pgvector extension enabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready!")
    
    yield
    
    print("👋 Shutting down...")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan
)

app.include_router(router)