"""
events.py
---------
FastAPI router for event persistence and history — Vision2Schedule Phase 4.

Endpoints:
    POST /events      — Save a structured event to the database
    GET  /events      — Retrieve history of saved events for the current user
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Event, User
from schemas import EventCreate, EventOut
from security import get_current_user

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a structured event to the database.
    """
    # Linking to user and storing confidence_score
    db_event = Event(
        **event_in.model_dump(),
        user_id=current_user.id
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventOut])
def get_user_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all events for the logged-in user.
    """
    events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id)
        .order_by(Event.created_at.desc())
        .all()
    )
    return events


