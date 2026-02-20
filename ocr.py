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
from fastapi import HTTPException, UploadFile
from starlette import status

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
# Public Interface
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
    # Step 1: Read file bytes into memory
    image_bytes: bytes = await file.read()

    # Step 2: Validate file type + size (implemented fully in commit 4)
    _validate_file(file, len(image_bytes))

    logger.info(
        "Starting OCR extraction | file=%s | size=%d bytes | type=%s",
        file.filename,
        len(image_bytes),
        file.content_type,
    )

    # Step 3: Call OCR.Space API
    raw_response = await _call_ocr_space_api(
        image_bytes=image_bytes,
        filename=file.filename or "upload.png",
        content_type=file.content_type or "image/png",
    )

    # Step 4: Parse and return structured result
    result = _parse_ocr_response(raw_response)

    logger.info(
        "OCR extraction complete | file=%s | word_count=%d",
        file.filename,
        result.get("word_count", 0),
    )

    return result


async def _call_ocr_space_api(
    image_bytes: bytes,
    filename: str,
    content_type: str,
) -> dict:
    """
    Send image bytes to the OCR.Space REST API via async HTTP POST.

    Uses multipart/form-data exactly as required by the OCR.Space API spec:
    https://ocr.space/ocrapi#PostFile

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
    if not OCR_SPACE_API_KEY:
        logger.error("OCR_SPACE_API_KEY is not set in environment variables.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR service is not configured. Contact the administrator.",
        )

    # Build multipart form payload as required by OCR.Space API
    form_data = {
        "apikey": OCR_SPACE_API_KEY,
        "language": OCR_SPACE_LANGUAGE,
        "isOverlayRequired": "false",   # We only need the parsed text, not bounding boxes
        "detectOrientation": "true",    # Auto-correct rotated flyers
        "scale": "true",               # Upscale low-resolution images for better accuracy
        "OCREngine": "2",              # Engine 2: better for complex layouts and mixed fonts
        "isSearchablePdfHideTextLayer": "false",
    }

    files = {
        "file": (filename, image_bytes, content_type),
    }

    try:
        async with httpx.AsyncClient(timeout=OCR_SPACE_TIMEOUT) as client:
            logger.debug("Sending image to OCR.Space API | engine=2 | lang=%s", OCR_SPACE_LANGUAGE)

            response = await client.post(
                OCR_SPACE_API_URL,
                data=form_data,
                files=files,
            )

            response.raise_for_status()   # Raises httpx.HTTPStatusError on 4xx/5xx
            response_json: dict = response.json()

            logger.debug("OCR.Space raw response received | status=%d", response.status_code)
            return response_json

    except httpx.TimeoutException:
        logger.error("OCR.Space API timed out after %d seconds.", OCR_SPACE_TIMEOUT)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OCR.Space API timed out after {OCR_SPACE_TIMEOUT} seconds. Please try again.",
        )

    except httpx.NetworkError as exc:
        logger.error("OCR.Space network error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot reach OCR.Space API. Check your internet connection.",
        )

    except httpx.HTTPStatusError as exc:
        logger.error("OCR.Space HTTP error: %s %s", exc.response.status_code, exc.response.text)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OCR.Space API returned an error: {exc.response.status_code}",
        )


def _parse_ocr_response(response: dict) -> dict:
    """
    Extract meaningful fields from the raw OCR.Space JSON response.

    OCR.Space response structure:
    {
        "ParsedResults": [
            {
                "ParsedText": "...",
                "ErrorMessage": "",
                "ErrorDetails": "",
                "TextOverlay": {...},
                "OCRExitCode": 1,
            }
        ],
        "OCRExitCode": 1,
        "IsErroredOnProcessing": false,
        "ProcessingTimeInMilliseconds": "531",
        "SearchablePDFURL": "...",
    }

    Args:
        response: Raw dict from OCR.Space API.

    Returns:
        Cleaned dict with raw_text, word_count, ocr_engine, is_searchable.

    Raises:
        HTTPException 422: IsErroredOnProcessing is True or no parsed text found.
    """
    # Check for API-level processing error
    if response.get("IsErroredOnProcessing", False):
        error_msg = response.get("ErrorMessage", ["Unknown OCR processing error."])
        if isinstance(error_msg, list):
            error_msg = " ".join(error_msg)
        logger.error("OCR.Space processing error: %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"OCR processing failed: {error_msg}",
        )

    parsed_results: list = response.get("ParsedResults", [])

    if not parsed_results:
        logger.warning("OCR.Space returned empty ParsedResults.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="OCR returned no results. The image may be blank, corrupted, or unreadable.",
        )

    # Concatenate all parsed text blocks (handles multi-page PDFs)
    raw_text: str = "\n".join(
        result.get("ParsedText", "").strip()
        for result in parsed_results
        if result.get("ParsedText", "").strip()
    )

    if not raw_text:
        logger.warning("OCR.Space returned results but parsed text is empty.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in the image. Try a higher-resolution photo.",
        )

    word_count: int = len(raw_text.split())

    # OCRExitCode 1 = parsed successfully
    ocr_exit_code: int = response.get("OCRExitCode", -1)

    # SearchablePDFURL is only present for PDF inputs
    is_searchable: bool = bool(response.get("SearchablePDFURL"))

    return {
        "raw_text": raw_text,
        "word_count": word_count,
        "ocr_exit_code": ocr_exit_code,
        "is_searchable": is_searchable,
        "processing_time_ms": response.get("ProcessingTimeInMilliseconds", "N/A"),
    }


def _validate_file(file: UploadFile, file_size: int) -> None:
    """
    Validate uploaded file type and size before sending to OCR.

    Checks run in order:
    1. File has content (not zero bytes)
    2. MIME type is in the allowed set
    3. File size does not exceed MAX_FILE_SIZE_BYTES (5 MB)

    Args:
        file      : FastAPI UploadFile object.
        file_size : Size of the file in bytes (measured after reading).

    Raises:
        HTTPException 400: File is empty.
        HTTPException 415: Unsupported MIME type / content type.
        HTTPException 413: File exceeds the 5 MB limit.
    """
    # Guard 1: Empty file body
    if file_size == 0:
        logger.warning("Rejected upload: zero-byte file | filename=%s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty. Please upload a valid flyer image.",
        )

    # Guard 2: MIME type allowlist
    content_type: str = (file.content_type or "").lower().split(";")[0].strip()
    if content_type not in ALLOWED_MIME_TYPES:
        logger.warning(
            "Rejected upload: unsupported MIME type | type=%s | filename=%s",
            content_type,
            file.filename,
        )
        allowed_list = ", ".join(sorted(ALLOWED_MIME_TYPES))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type: '{content_type}'. "
                f"Allowed types: {allowed_list}"
            ),
        )

    # Guard 3: File size limit (5 MB — OCR.Space free tier)
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        logger.warning(
            "Rejected upload: file too large | size=%.2f MB | limit=%.0f MB | filename=%s",
            size_mb,
            max_mb,
            file.filename,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File is too large ({size_mb:.2f} MB). "
                f"Maximum allowed size is {max_mb:.0f} MB."
            ),
        )

    logger.debug(
        "File validation passed | filename=%s | size=%d bytes | type=%s",
        file.filename,
        file_size,
        content_type,
    )
