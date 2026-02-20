"""
extract.py
----------
Text Extraction Engine for Vision2Schedule — Phase 3.

Responsibilities:
- Parse raw OCR text output into structured event fields
- Use Regex patterns for deterministic field extraction
- Use spaCy NER for semantic entity detection (location, organization)
- Return a unified structured event dictionary

Extraction targets:
    - title      : Event name (spaCy ORG or first capitalised line)
    - date       : Event date (Regex, multiple formats)
    - time       : Event start time (Regex, 12h/24h)
    - venue      : Location (spaCy GPE/LOC + Regex fallback)
    - organizer  : Hosting organisation (spaCy ORG)
    - contact    : Phone number (Regex E.164 / local formats)
    - website    : URL (Regex)
    - category   : Keyword-based classification

Required pip packages:
    pip install spacy
    python -m spacy download en_core_web_sm
"""

import re
import logging
from typing import Optional

import spacy

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load spaCy model
# ---------------------------------------------------------------------------
# en_core_web_sm: small English model — efficient for NER on short flyer text.
# Falls back gracefully if model is not installed.
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    nlp = None
    logger.warning(
        "spaCy model 'en_core_web_sm' not found. "
        "Run: python -m spacy download en_core_web_sm"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_event_data(raw_text: str) -> dict:
    """
    Main entry point — parse all event fields from raw OCR text.

    Args:
        raw_text: Full string of text extracted by OCR.Space.

    Returns:
        Structured event dict with keys:
        title, date, time, venue, organizer, contact, website, category.
        Any field that could not be extracted will be None.
    """
    pass  # Implemented in commit 5 (assembly)


# ---------------------------------------------------------------------------
# Internal extraction stubs — implemented per-commit
# ---------------------------------------------------------------------------

def _extract_date(text: str) -> Optional[str]:
    """Extract the first recognisable event date from text. → Commit 2"""
    pass


def _extract_time(text: str) -> Optional[str]:
    """Extract the first recognisable event start time from text. → Commit 2"""
    pass


def _extract_phone(text: str) -> Optional[str]:
    """Extract a phone/contact number from text. → Commit 3"""
    pass


def _extract_website(text: str) -> Optional[str]:
    """Extract the first URL from text. → Commit 3"""
    pass


def _extract_location(text: str) -> Optional[str]:
    """Use spaCy GPE/LOC entities to find venue. → Commit 4"""
    pass


def _extract_organization(text: str) -> Optional[str]:
    """Use spaCy ORG entities to find organizer / event title. → Commit 4"""
    pass


def _classify_category(text: str) -> Optional[str]:
    """Keyword-based event category classifier. → Commit 5"""
    pass
