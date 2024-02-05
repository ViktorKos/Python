from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate, NoteResponse
from src.repository import notes as repository_notes


router = APIRouter(prefix='/notes', tags=["notes"])


@router.get("/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = await repository_notes.get_notes(skip, limit, db)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = await repository_notes.get_note(note_id, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/", response_model=NoteResponse)
async def create_note(body: NoteModel, db: Session = Depends(get_db)):
    return await repository_notes.create_note(body, db)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(body: NoteUpdate, note_id: int, db: Session = Depends(get_db)):
    note = await repository_notes.update_note(note_id, body, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_status_note(body: NoteStatusUpdate, note_id: int, db: Session = Depends(get_db)):
    note = await repository_notes.update_status_note(note_id, body, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.delete("/{note_id}", response_model=NoteResponse)
async def remove_note(note_id: int, db: Session = Depends(get_db)):
    note = await repository_notes.remove_note(note_id, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note