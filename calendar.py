"""
calendar.py
-----------
Calendar service for Vision2Schedule — Phase 6.

Responsibilities:
- Generate .ics files for event downloads.
- Provide endpoints for Google Calendar sync.
- Validate datetime strings before scheduling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from datetime import datetime, date, time
import icalendar
from typing import Optional

from security import get_current_user
from models import User

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)

def validate_event_datetime(event_date: Optional[date], event_time: Optional[time]) -> datetime:
    """
    Validate and combine date and time into a single datetime object.
    
    Args:
        event_date: Date object
        event_time: Time object
        
    Returns:
        datetime: Combined datetime object
        
    Raises:
        HTTPException: If date is missing
    """
    if not event_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event date is required for calendar scheduling."
        )
    
    t = event_time if event_time else time(0, 0)
    return datetime.combine(event_date, t)
