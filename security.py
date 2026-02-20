"""
security.py
-----------
Core security utilities for Vision2Schedule.

Responsibilities:
- Password hashing and verification via bcrypt (passlib)
- JWT access token creation (python-jose)
- JWT verification and decoding
- FastAPI dependency: get_current_user — injects the authenticated user
  into any protected route via Depends()

No business logic lives here — pure utility functions only.

Required environment variables (.env):
    JWT_SECRET_KEY   : Strong random secret for signing tokens
    JWT_ALGORITHM    : e.g. "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : e.g. 60
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import TokenData

# ---------------------------------------------------------------------------
# Load environment config
# ---------------------------------------------------------------------------
load_dotenv()

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "changeme-use-a-strong-secret-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------
# CryptContext wraps bcrypt — handles hashing, salt generation, and verification.
# deprecated="auto" will auto-upgrade legacy hashes on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The raw password string from the user.

    Returns:
        A bcrypt hash string (60+ chars), safe to store in the DB.

    Example:
        hashed = hash_password("MySecret123")
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password  : Raw password from login form.
        hashed_password : Stored bcrypt hash from the DB.

    Returns:
        True if they match, False otherwise.

    Example:
        is_valid = verify_password("MySecret123", stored_hash)
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT Token Creation
# ---------------------------------------------------------------------------
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data         : Payload dict — must include a "sub" key (subject).
                       We use {"sub": str(user_id), "email": email}.
        expires_delta: Optional custom lifetime. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        A signed JWT string to return to the client as a Bearer token.

    Example:
        token = create_access_token(data={"sub": "42", "email": "user@example.com"})
    """
    payload = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# ---------------------------------------------------------------------------
# JWT Token Decoding
# ---------------------------------------------------------------------------
def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: Raw JWT string from the Authorization header.

    Returns:
        TokenData with user_id and email extracted from the payload.

    Raises:
        HTTPException 401: If the token is invalid, expired, or malformed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Token is invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")

        if user_id is None:
            raise credentials_exception

        return TokenData(user_id=int(user_id), email=email)

    except JWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# OAuth2 Bearer Scheme
# ---------------------------------------------------------------------------
# Tells FastAPI to look for a Bearer token in the Authorization header.
# tokenUrl="/auth/login" makes this visible in the /docs Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# FastAPI Dependency: get_current_user
# ---------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the current authenticated user.

    Flow:
    1. Extracts the Bearer token from the Authorization header.
    2. Decodes and validates the JWT.
    3. Looks up the user in the database.
    4. Returns the User ORM object.

    Raises:
        HTTPException 401: If token is invalid or user no longer exists.

    Usage in a protected route:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"email": current_user.email}
    """
    token_data = decode_access_token(token)

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
