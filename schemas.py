"""
schemas.py
----------
Pydantic v2 schemas for Vision2Schedule API.

Defines:
- User schemas   : UserCreate, UserLogin, UserOut
- Event schemas  : EventCreate, EventUpdate, EventOut
- Token schemas  : Token, TokenData

Separation of concerns:
- *Create schemas : validate incoming request body fields
- *Out schemas    : shape API response — never expose password_hash
- *Update schemas : allow partial updates (all fields Optional)

These schemas are completely decoupled from SQLAlchemy models —
they serve as the API contract layer only.
"""

from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ===========================================================================
# USER SCHEMAS
# ===========================================================================

class UserCreate(BaseModel):
    """
    Schema for POST /auth/register
    Validates incoming registration payload.
    """
    email: EmailStr = Field(
        ...,
        description="Valid email address — used as login identifier"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Plain-text password (min 8 chars). Hashed before storage."
    )

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        """Normalize email to lowercase before any DB operation."""
        return v.lower().strip()


class UserLogin(BaseModel):
    """
    Schema for POST /auth/login
    Validates login credentials.
    """
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()


class UserOut(BaseModel):
    """
    Schema for API responses involving user data.
    Deliberately omits password_hash.
    """
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}   # Enables ORM mode (Pydantic v2)


# ===========================================================================
# TOKEN SCHEMAS
# ===========================================================================

class Token(BaseModel):
    """
    Response body returned after a successful login.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Decoded payload extracted from a JWT.
    Used internally by the auth dependency.
    """
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None


# ===========================================================================
# EVENT SCHEMAS
# ===========================================================================

class EventCreate(BaseModel):
    """
    Schema for POST /events
    All fields except title are optional — mirrors nullable DB columns.
    Confidence score is computed server-side, not accepted from the client.
    """
    title: str = Field(
        ...,
        max_length=300,
        description="Event name/title"
    )
    date: Optional[date] = Field(
        None,
        description="Event date in YYYY-MM-DD format"
    )
    time: Optional[time] = Field(
        None,
        description="Event start time in HH:MM:SS format"
    )
    venue: Optional[str] = Field(
        None,
        max_length=500,
        description="Venue or location string"
    )
    organizer: Optional[str] = Field(
        None,
        max_length=300,
        description="Organizer or host name"
    )
    contact: Optional[str] = Field(
        None,
        max_length=300,
        description="Contact info — phone, email, or social handle"
    )
    website: Optional[str] = Field(
        None,
        max_length=2083,
        description="Event website URL"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Event category e.g. Concert, Workshop, Sports"
    )


class EventUpdate(BaseModel):
    """
    Schema for PATCH /events/{event_id}
    All fields fully optional — supports partial updates.
    """
    title: Optional[str] = Field(None, max_length=300)
    date: Optional[date] = None
    time: Optional[time] = None
    venue: Optional[str] = Field(None, max_length=500)
    organizer: Optional[str] = Field(None, max_length=300)
    contact: Optional[str] = Field(None, max_length=300)
    website: Optional[str] = Field(None, max_length=2083)
    category: Optional[str] = Field(None, max_length=100)


class EventOut(BaseModel):
    """
    Schema for API responses involving event data.
    Includes computed fields (id, user_id, confidence_score, created_at).
    """
    id: int
    user_id: int
    title: str
    date: Optional[date]
    time: Optional[time]
    venue: Optional[str]
    organizer: Optional[str]
    contact: Optional[str]
    website: Optional[str]
    category: Optional[str]
    confidence_score: Decimal = Field(
        ...,
        description="Extraction confidence score (90.00–100.00)"
    )
    created_at: datetime

    model_config = {"from_attributes": True}   # Enables ORM mode (Pydantic v2)
