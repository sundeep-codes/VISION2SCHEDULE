"""
ocr.py
------
OCR Service for Vision2Schedule — Phase 2.

Responsibilities:
- Accept an uploaded image file from the FastAPI endpoint
- Send the image to the OCR.Space API via async HTTP (httpx)
- Parse and return structured OCR text output
- Raise descriptive errors on API failures

External dependency:
    OCR.Space API — https://ocr.space/ocrapi
    Requires: OCR_SPACE_API_KEY in .env

Supported formats:
    JPEG, JPG, PNG, GIF, BMP, TIFF, WEBP, PDF (single page)

Required .env variables:
    OCR_SPACE_API_KEY       : Your OCR.Space API key (free tier: K_xxxxxxxx)
    OCR_SPACE_LANGUAGE      : Language code, default "eng"
    OCR_SPACE_TIMEOUT       : Request timeout in seconds, default 30
"""

import os
import logging
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import UploadFile

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OCR_SPACE_API_URL: str = "https://api.ocr.space/parse/image"

OCR_SPACE_API_KEY: str = os.getenv("OCR_SPACE_API_KEY", "")
OCR_SPACE_LANGUAGE: str = os.getenv("OCR_SPACE_LANGUAGE", "eng")
OCR_SPACE_TIMEOUT: int = int(os.getenv("OCR_SPACE_TIMEOUT", "30"))

# Allowed MIME types for uploaded flyer images
ALLOWED_MIME_TYPES: set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/webp",
    "application/pdf",
}

# Max file size: 5 MB (OCR.Space free tier limit)
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public Interface (stubs — implemented in subsequent commits)
# ---------------------------------------------------------------------------

async def extract_text_from_image(file: UploadFile) -> dict:
    """
    Main entry point for the OCR pipeline.

    Validates the uploaded file, sends it to OCR.Space,
    and returns a structured dict with the extracted text.

    Args:
        file: FastAPI UploadFile from a multipart/form-data POST request.

    Returns:
        {
            "raw_text"     : str   — full extracted text,
            "word_count"   : int   — number of words in extracted text,
            "ocr_engine"   : int   — OCR engine used (1 or 2),
            "is_searchable": bool  — whether the PDF/image was searchable,
        }

    Raises:
        HTTPException 400: Unsupported file type or file too large.
        HTTPException 422: OCR.Space returned an error or empty result.
        HTTPException 503: OCR.Space API is unreachable.
    """
    pass  # Implemented in next commit


async def _call_ocr_space_api(
    image_bytes: bytes,
    filename: str,
    content_type: str,
) -> dict:
    """
    Send image bytes to the OCR.Space REST API via async HTTP POST.

    Args:
        image_bytes  : Raw bytes of the uploaded image.
        filename     : Original filename (used for MIME detection on the API side).
        content_type : MIME type string (e.g. "image/png").

    Returns:
        Raw JSON response dict from OCR.Space API.

    Raises:
        HTTPException 503: Network failure or API timeout.
        HTTPException 422: API returned IsErroredOnProcessing = True.
    """
    pass  # Implemented in next commit


def _parse_ocr_response(response: dict) -> dict:
    """
    Extract meaningful fields from the raw OCR.Space JSON response.

    Args:
        response: Raw dict from OCR.Space API.

    Returns:
        Cleaned dict with raw_text, word_count, ocr_engine, is_searchable.

    Raises:
        HTTPException 422: No parsed results in response body.
    """
    pass  # Implemented in next commit


def _validate_file(file: UploadFile, file_size: int) -> None:
    """
    Validate uploaded file type and size before sending to OCR.

    Args:
        file      : FastAPI UploadFile object.
        file_size : Size of the file in bytes.

    Raises:
        HTTPException 400: Unsupported MIME type.
        HTTPException 413: File exceeds the 5 MB limit.
    """
    pass  # Implemented in error handling commit
