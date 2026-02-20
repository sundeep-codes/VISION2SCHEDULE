"""
models.py
---------
SQLAlchemy ORM models for Vision2Schedule.

Defines:
- User  : Registered application user
- Event : Scanned event linked to a user (one-to-many)

Each model maps directly to a MySQL table.
Tables are created via: Base.metadata.create_all(bind=engine)
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Date,
    Time,
    DateTime,
    DECIMAL,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from database import Base


# ---------------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------------
class User(Base):
    """
    Represents a registered user of Vision2Schedule.

    Table: users
    """

    __tablename__ = "users"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Surrogate primary key"
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique user email used for login"
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="bcrypt hashed password — raw password never stored"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="UTC timestamp of account creation"
    )

    # -----------------------------------------------------------------------
    # Relationship
    # -----------------------------------------------------------------------
    # One User → Many Events
    # cascade="all, delete-orphan" ensures events are deleted when user is deleted
    events = relationship(
        "Event",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",         # Returns a query object — efficient for large sets
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


# ---------------------------------------------------------------------------
# Event Model
# ---------------------------------------------------------------------------
class Event(Base):
    """
    Represents an event extracted from a scanned flyer image.

    Table: events
    Most extraction fields are nullable — a scan is valid even if
    only a subset of fields were successfully parsed by OCR + NLP.
    The confidence_score reflects extraction completeness.
    """

    __tablename__ = "events"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Surrogate primary key"
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to users.id — scopes event to its owner"
    )

    title = Column(
        String(300),
        nullable=False,
        comment="Event name/title extracted from flyer"
    )

    date = Column(
        Date,
        nullable=True,
        comment="Event date (YYYY-MM-DD). Nullable if OCR could not extract it."
    )

    time = Column(
        Time,
        nullable=True,
        comment="Event start time (HH:MM:SS). Nullable for all-day or ambiguous events."
    )

    venue = Column(
        String(500),
        nullable=True,
        comment="Raw or Google Places-enriched venue/location string"
    )

    organizer = Column(
        String(300),
        nullable=True,
        comment="Name of the event host or organizer"
    )

    contact = Column(
        String(300),
        nullable=True,
        comment="Contact info (phone, email, or social handle) from the flyer"
    )

    website = Column(
        String(2083),
        nullable=True,
        comment="Event URL (2083 = safe max URL length)"
    )

    category = Column(
        String(100),
        nullable=True,
        comment="Event category e.g. Concert, Workshop, Sports, Conference"
    )

    confidence_score = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=90.00,
        comment="Deterministic OCR extraction confidence score (90.00–100.00)"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="UTC timestamp of event record creation"
    )

    # -----------------------------------------------------------------------
    # Relationship
    # -----------------------------------------------------------------------
    # Many Events → One User
    owner = relationship(
        "User",
        back_populates="events",
    )

    def __repr__(self):
        return f"<Event id={self.id} title={self.title} user_id={self.user_id}>"
