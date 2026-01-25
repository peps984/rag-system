from pydantic import BaseModel
from datetime import datetime
from typing import List

# schema for documents
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    uploaded_at: datetime
    content_length: int | None = None
    
    class Config:
        from_attributes = True

class DocumentWithContent(DocumentResponse):
    content: str | None = None

class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    char_count: int
    
    class Config:
        from_attributes = True
class DocumentWithChunks(DocumentResponse):
    chunks: list[ChunkResponse] = []

class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    char_count: int
    similarity: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int

class SourceReference(BaseModel):
    document_id: int
    chunk_index: int
    content: str
    similarity: float

class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceReference]
    model_used: str = "gpt-4o-mini"