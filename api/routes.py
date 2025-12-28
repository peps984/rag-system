from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path
from database.database import get_db
from database.models import Note, Document, DocumentChunk
from api.schemas import NoteCreate, NoteResponse, NoteUpdate, DocumentResponse, DocumentWithContent, DocumentWithChunks
from config.settings import UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP
from processing.text_extractor import text_extractor
from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/about")
async def about():
    from config.settings import APP_NAME, APP_VERSION
    return {"name": APP_NAME, "version": APP_VERSION}

@router.post("/notes", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """
    create a new note
    """
    db_note = Note(
        title=note.title,
        content=note.content
    )
    
    db.add(db_note)
    
    db.commit()
    
    db.refresh(db_note)
    
    return db_note

@router.get("/notes", response_model=List[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    """
    Get all the notes
    """
    notes = db.query(Note).all()
    return notes

@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Get a single note by ID
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}

@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)):
    """
    Update a note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note_update.title is not None:
        note.title = note_update.title
    
    if note_update.content is not None:
        note.content = note_update.content
    
    db.commit()
    db.refresh(note)
    
    return note

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document and split it in chunks
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
        print(f"Warning: Could not extract text: {e}")
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