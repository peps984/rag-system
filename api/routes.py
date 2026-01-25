from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path
from database.database import get_db
from database.models import Document, DocumentChunk
from api.schemas import DocumentResponse, DocumentWithContent, DocumentWithChunks, SearchResponse, SearchResult, RAGResponse
from config.settings import APP_NAME, APP_VERSION, UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP
from processing.text_extractor import text_extractor
from processing.embedding_generator import EmbeddingGenerator
from processing.similarity_search import SimilaritySearch
from processing.rag_service import RAGService
from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter()

@router.get("/")
def root():
    """
    Root endpoint - API information and navigation
    """
    return {
        "message": "Welcome to RAG Production System API",
        "version": APP_VERSION,
        "status": "operational",
        "documentation": {
            "interactive": "/docs",
            "alternative": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "upload": "/documents/upload",
            "search": "/search",
            "query": "/query"
        },
        "repository": "https://github.com/peps984/rag-system"
    }

@router.get("/about")
async def about():
    return {"name": APP_NAME, "version": APP_VERSION}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    generate_embeddings: bool = True,
    db: Session = Depends(get_db)
):
    """
    Upload a document, split it in chunks and generate embeddings
    """
    
    # extension validation
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
            )
    
    # file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # size validation
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceed the limit. Max size allowed: {MAX_FILE_SIZE_MB}MB"
            )
    
    # generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # extract text
    try:
        extracted_text = text_extractor(file_path)
        content_length = len(extracted_text)
    except Exception as e:
        print(f"Warning: could not extract text: {e}")
        extracted_text = None
        content_length = 0
    
    # write document metadata on db
    db_document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_type=file_extension,
        content=extracted_text,
        content_length=content_length
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    if extracted_text:
        chunker = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        chunks = chunker.split_text(extracted_text)
        
        for idx, chunk_data in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=db_document.id,
                chunk_index=idx,
                content=chunk_data,
                char_count=len(chunk_data)
            )
            db.add(db_chunk)
        
        db.commit()
    
    if (generate_embeddings and extracted_text):
        try:
            generator = EmbeddingGenerator()
            
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == db_document.id).all()
            texts = [chunk.content for chunk in chunks]
            embeddings = generator.generate_embeddings_batch(texts)
            
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            
            db.commit()
            
            print(f"generated embeddings for {len(chunks)} chunks")
        
        except Exception as e:
            print(f"warning: could not generate embeddings: {e}")
            
    return db_document

@router.get("/documents", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """
    Get a list of all the documents
    """
    documents = db.query(Document).all()
    return documents

@router.get("/documents/{document_id}", response_model=DocumentWithContent)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get a single document by ID
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.get("/documents/search/{query}")
def search_documents(query: str, db: Session = Depends(get_db)):
    """
    Search for documents that contain query
    """
    documents = db.query(Document).filter(
        Document.content.ilike(f"%{query}%")
    ).all()
    
    return documents

@router.get("/documents/{document_id}/chunks", response_model=DocumentWithChunks)
def get_document_with_chunks(document_id: int, db: Session = Depends(get_db)):
    """
    Get a document with all the chunks
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.post("/documents/{document_id}/generate-embeddings")
def generate_embeddings_for_document(document_id: int, db: Session = Depends(get_db)):
    """
    Generate embeddings of all the chunks of a document
    """
    # Check if document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunks
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found")
    
    # Generate embeddings
    generator = EmbeddingGenerator()
    
    texts = [chunk.content for chunk in chunks]
    embeddings = generator.generate_embeddings_batch(texts)
    
    # Save embeddings
    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding
    
    db.commit()
    
    return {
        "document_id": document_id,
        "chunks_processed": len(chunks),
        "message": "Embeddings generated successfully"
    }


@router.post("/search", response_model=SearchResponse)
def search_documents(
    query: str,
    top_k: int = 5,
    document_id: int = None,
    min_similarity: float = 0.3,
    db: Session = Depends(get_db)
):
    """
    Search for chunks related to query
    """
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    searcher = SimilaritySearch(db)
    results = searcher.search(query=query, top_k=top_k, document_id=document_id)
    
    # show results only if above a similarity threshold
    results = [r for r in results if r["similarity"] >= min_similarity]
    
    return {
        "query": query,
        "results": results,
        "total_results": len(results)
    }

@router.post("/query", response_model=RAGResponse)
def rag_query(
    question: str,
    top_k: int = 5,
    document_id: int = None,
    model: str = "gpt-4o-mini",
    db: Session = Depends(get_db)
):
    """
    Execute the RAG query
    """
    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    rag_service = RAGService(db)
    result = rag_service.query(
        question=question,
        top_k=top_k,
        document_id=document_id,
        model=model
    )
    
    return result