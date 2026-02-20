"""
auth.py
-------
FastAPI router for authentication endpoints in Vision2Schedule.

Endpoints:
    POST /auth/register  — Create a new user account
    POST /auth/login     — Authenticate and return a JWT access token

Design rules:
- Routers stay thin: validate input → call service/utility → return response
- No raw password ever touches the DB — always hashed via security.py
- Consistent error responses with appropriate HTTP status codes
- Email is normalized (lowercased) by the Pydantic schema before hitting this router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserOut, Token
from security import hash_password, verify_password, create_access_token

# ---------------------------------------------------------------------------
# Router Setup
# ---------------------------------------------------------------------------
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new Vision2Schedule user account. "
        "Returns the created user object (without password). "
        "Raises 409 if the email is already registered."
    ),
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register endpoint.

    Steps:
    1. Check if the email already exists in the DB (case-insensitive via schema normalization).
    2. Hash the plain-text password using bcrypt.
    3. Persist the new user to the database.
    4. Return the serialized UserOut (no password hash in response).

    Args:
        user_data : Validated UserCreate payload (email + password).
        db        : Injected SQLAlchemy session via Depends(get_db).

    Returns:
        UserOut: id, email, created_at.

    Raises:
        409 Conflict: Email already registered.
    """
    # Step 1: Duplicate email check
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{user_data.email}' already exists.",
        )

    # Step 2: Hash the password — raw password discarded after this point
    hashed = hash_password(user_data.password)

    # Step 3: Persist new user
    new_user = User(
        email=user_data.email,
        password_hash=hashed,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)   # Reload from DB to populate auto-generated fields (id, created_at)

    # Step 4: Return serialized response (UserOut omits password_hash)
    return new_user


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login and receive a JWT access token",
    description=(
        "Authenticates a user with email and password. "
        "Returns a Bearer JWT token valid for the configured expiry window. "
        "Use this token in the Authorization header for all protected endpoints."
    ),
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint.

    Steps:
    1. Look up the user by email.
    2. Verify the provided password against the stored bcrypt hash.
    3. Generate a JWT access token with user_id and email as claims.
    4. Return the token and type.

    Security note:
        We return the SAME generic error for "user not found" and "wrong password"
        to prevent user enumeration attacks.

    Args:
        credentials : Validated UserLogin payload (email + password).
        db          : Injected SQLAlchemy session via Depends(get_db).

    Returns:
        Token: { access_token: "...", token_type: "bearer" }

    Raises:
        401 Unauthorized: Invalid email or password.
    """
    # Shared exception for both "no user" and "wrong password" — prevents enumeration
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password. Please try again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1: Fetch user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise auth_exception

    # Step 2: Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise auth_exception

    # Step 3: Build JWT payload and create token
    token = create_access_token(
        data={
            "sub": str(user.id),     # "sub" (subject) is the JWT standard claim for user identity
            "email": user.email,
        }
    )

    # Step 4: Return token response
    return Token(access_token=token, token_type="bearer")
