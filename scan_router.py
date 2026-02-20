"""
scan_router.py
--------------
FastAPI router for image upload and OCR scanning — Vision2Schedule Phase 2.

Endpoints:
    POST /scan       — Upload a flyer image, run OCR, return extracted text
    GET  /scan/{id}  — Retrieve a previous scan result by scan ID (stub for Phase 3)

Design rules:
- Route handler is thin: validate auth → delegate to ocr.py service → persist → respond
- Authentication required on all endpoints via get_current_user dependency
- Accept multipart/form-data with a single "file" field
- Return structured JSON with raw OCR text and metadata
"""

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from database import get_db
from models import User
from ocr import extract_text_from_image
from security import get_current_user

# ---------------------------------------------------------------------------
# Router Setup
# ---------------------------------------------------------------------------
router = APIRouter(
    prefix="/scan",
    tags=["OCR Scanning"],
)


# ---------------------------------------------------------------------------
# POST /scan
# ---------------------------------------------------------------------------
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Upload a flyer image and extract text via OCR",
    description=(
        "Accepts a flyer image (JPEG, PNG, WEBP, PDF, etc.) as multipart/form-data. "
        "Sends the image to the OCR.Space API and returns the extracted raw text "
        "along with extraction metadata. Requires a valid Bearer token."
    ),
    response_description="Extracted OCR text and processing metadata",
)
async def scan_image(
    file: UploadFile = File(
        ...,
        description="Flyer image file (JPEG/PNG/WEBP/PDF, max 5 MB)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Scan endpoint — OCR pipeline entry point.

    Flow:
    1. Authenticate user via JWT (get_current_user dependency).
    2. Validate the uploaded file type and size (inside extract_text_from_image).
    3. Send image to OCR.Space API and get extracted text.
    4. Return structured response with raw text and metadata.
       (Persistence to DB and extraction engine wired in Phase 3.)

    Args:
        file         : Uploaded image from multipart/form-data.
        db           : Injected DB session (used in Phase 3 for persistence).
        current_user : Authenticated User ORM object from JWT.

    Returns:
        JSON with raw_text, word_count, processing metadata, and user context.

    Raises:
        400: Unsupported file type or missing file.
        401: Missing or invalid Bearer token.
        413: File exceeds 5 MB limit.
        422: OCR.Space returned no readable text.
        503: OCR.Space API unreachable or not configured.
    """
    # Reject requests with no filename (empty file field submitted)
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file was uploaded. Please attach a flyer image.",
        )

    # Delegate OCR processing entirely to the service layer
    ocr_result = await extract_text_from_image(file)

    return {
        "status": "success",
        "message": "OCR extraction completed successfully.",
        "scanned_by": current_user.email,
        "scanned_at": datetime.utcnow().isoformat() + "Z",
        "file_name": file.filename,
        "ocr_result": ocr_result,
    }


# ---------------------------------------------------------------------------
# GET /scan/{scan_id}  — stub for Phase 3
# ---------------------------------------------------------------------------
@router.get(
    "/{scan_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve a previous scan result",
    description=(
        "Returns a previously saved scan and its extracted event data. "
        "Full implementation in Phase 3 when DB persistence is wired."
    ),
)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Stub — will query the scans table and return stored OCR + extracted data.
    Fully implemented in Phase 3.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scan retrieval will be available in Phase 3.",
    )
