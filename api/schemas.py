from pydantic import BaseModel
from datetime import datetime

# schema for note creation
class NoteCreate(BaseModel):
    title: str
    content: str

# schema for answer
class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# schema for note update
class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None