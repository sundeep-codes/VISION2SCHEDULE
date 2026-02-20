from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from security import get_current_user
from models import User
from nearby import get_nearby_events

router = APIRouter(
    prefix="/nearby",
    tags=["Nearby Events"],
)

@router.get("/", response_model=List[dict])
def search_nearby(
    venue: str = Query(..., description="The venue or address to search near"),
    category: Optional[str] = Query(None, description="Event category for filtering"),
    show_all: bool = Query(False, description="Whether to ignore category filtering"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for events near a specific venue.
    """
    try:
        events = get_nearby_events(venue, category, show_all)
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching nearby events: {str(e)}"
        )
