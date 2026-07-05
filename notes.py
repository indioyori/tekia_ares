from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.note import Note
from app.models.tag import Tag
from app.services.note_service import NoteService
from app.services.integration import RAGIntegration

router = APIRouter(prefix="/api/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str
    content: str
    theme: Optional[str] = None
    document_id: Optional[int] = None
    tags: Optional[List[str]] = []
    encrypted: bool = False


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    theme: Optional[str] = None
    tags: Optional[List[str]] = None


# /tags/ y /themes/ ANTES de /{id} para evitar colisión de rutas
@router.get("/tags/")
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.get("/themes/")
def list_themes(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT DISTINCT theme FROM notes WHERE theme IS NOT NULL")).fetchall()
    return [r[0] for r in rows]


@router.post("/from-document/{doc_id}")
def from_document(doc_id: int, analysis_type: str = "summary", db: Session = Depends(get_db)):
    return RAGIntegration(db).create_note_from_document(doc_id, analysis_type)


@router.post("/")
def create_note(body: NoteCreate, db: Session = Depends(get_db)):
    return NoteService(db).create_note(**body.model_dump())


@router.get("/")
def list_notes(query: Optional[str] = None, theme: Optional[str] = None,
               document_id: Optional[int] = None, db: Session = Depends(get_db)):
    return NoteService(db).get_notes(query=query, theme=theme, document_id=document_id)


@router.get("/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    return NoteService(db).get_note(note_id)


@router.put("/{note_id}")
def update_note(note_id: int, body: NoteUpdate, db: Session = Depends(get_db)):
    return NoteService(db).update_note(note_id, **{k: v for k, v in body.model_dump().items() if v is not None})


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    return {"deleted": NoteService(db).delete_note(note_id)}
