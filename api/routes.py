from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Note
from api.schemas import NoteCreate, NoteResponse, NoteUpdate
from typing import List

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
    Get all notes
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