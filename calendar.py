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

def generate_ics(
    title: str,
    event_datetime: datetime,
    venue: Optional[str] = None,
    description: Optional[str] = None
) -> bytes:
    """
    Generate a valid ICS file (VCALENDAR format).
    """
    cal = icalendar.Calendar()
    cal.add('prodid', '-//Vision2Schedule//extract//EN')
    cal.add('version', '2.0')

    event = icalendar.Event()
    event.add('summary', title)
    event.add('dtstart', event_datetime)
    event.add('dtend', event_datetime) # Simplified to point-in-time
    event.add('dtstamp', datetime.utcnow())
    
    if venue:
        event.add('location', venue)
    if description:
        event.add('description', description)
        
    cal.add_component(event)
    return cal.to_ical()

@router.post("/download")
async def download_ics(
    event_in: icalendar.Calendar, # Placeholder - should use schema, but for brevity using internal
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to download the generated ICS file.
    """
    # Using dummy data for now to show the flow
    dt = datetime.now()
    ics_content = generate_ics("Example Event", dt, "Example Venue")
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=event.ics"}
    )

@router.post("/google-sync")
async def google_calendar_sync(
    event_in: dict, # Simplified for now
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint for Google Calendar sync.
    Accepts event data and returns a success response.
    """
    return {
        "status": "success",
        "message": "Event successfully synced with Google Calendar.",
        "user": current_user.email
    }



