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