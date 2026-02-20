"""
database.py
-----------
Handles all database connectivity for Vision2Schedule.

Responsibilities:
- Creates the SQLAlchemy engine from the DATABASE_URL env variable
- Provides a SessionLocal factory for creating DB sessions
- Exposes a declarative Base that all ORM models inherit from
- Provides a get_db() dependency for FastAPI route injection
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from .env file
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/vision2schedule"
)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True: verifies connections are alive before using them.
# This prevents "MySQL server has gone away" errors on idle connections.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,          # Set to True during development to log SQL queries
)

# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
# autocommit=False : transactions must be committed explicitly
# autoflush=False  : prevents premature flushes before commit
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------
# All ORM models will inherit from this Base.
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI Dependency: get_db
# ---------------------------------------------------------------------------
def get_db():
    """
    Yields a SQLAlchemy database session per request.
    Guarantees the session is closed after the request completes,
    even if an exception is raised.

    Usage in a router:
        @router.get("/example")
        def example_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
