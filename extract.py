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
from confidence import calculate_confidence

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

    Orchestrates all extractor functions in order and assembles
    a single clean structured event dictionary ready for DB persistence
    or Eventbrite/Calendar sync.

    Args:
        raw_text: Full string of text extracted by OCR.Space.

    Returns:
        Structured event dict:
        {
            "title"      : str | None,
            "date"       : str | None,
            "time"       : str | None,
            "venue"      : str | None,
            "organizer"  : str | None,
            "contact"    : str | None,
            "website"    : str | None,
            "category"   : str | None,
        }
        Fields that could not be extracted are None.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("extract_event_data called with empty text.")
        return {
            "title": None, "date": None, "time": None,
            "venue": None, "organizer": None, "contact": None,
            "website": None, "category": None,
        }

    logger.info("Extracting event data from OCR text (%d chars)", len(raw_text))

    # Run all extractors
    date       = _extract_date(raw_text)
    time       = _extract_time(raw_text)
    phone      = _extract_phone(raw_text)
    website    = _extract_website(raw_text)
    venue      = _extract_location(raw_text)
    organizer  = _extract_organization(raw_text)
    category   = _classify_category(raw_text)

    # Title heuristic: use organizer if found, else first non-empty title-case line
    title: Optional[str] = None
    for line in raw_text.splitlines():
        stripped = line.strip()
        # A good title line is title-case or all-caps, between 4 and 80 chars,
        # and does not look like a date, URL, or phone number
        if (
            stripped
            and 4 <= len(stripped) <= 80
            and not re.search(r"\d{4}|http|www|\+\d", stripped)
            and (stripped.istitle() or stripped.isupper())
        ):
            title = stripped.title()
            break

    event = {
        "title"     : title,
        "date"      : date,
        "time"      : time,
        "venue"     : venue,
        "organizer" : organizer,
        "contact"   : phone,
        "website"   : website,
        "category"  : category,
    }

    # Attach confidence score (90-100%)
    event["confidence_score"] = calculate_confidence(event)

    extracted_count = sum(1 for v in event.values() if v is not None and v != event.get("confidence_score"))
    logger.info(
        "Extraction complete: %d/%d fields extracted | confidence: %.2f%%",
        extracted_count, len(event) - 1, event["confidence_score"]
    )

    return event



# ---------------------------------------------------------------------------
# Internal extraction stubs — implemented per-commit
# ---------------------------------------------------------------------------

def _extract_date(text: str) -> Optional[str]:
    """
    Extract the first recognisable event date from OCR text.

    Patterns covered (case-insensitive):
        - "January 5, 2025"  / "Jan 5 2025"
        - "5th January 2025" / "5 Jan 2025"
        - "05/01/2025"       / "05-01-2025"
        - "2025-01-05"       (ISO 8601)
        - "Friday, January 5" (day-of-week prefix)

    Args:
        text: Raw OCR text.

    Returns:
        Matched date string as found in the text, or None.
    """
    MONTHS = (
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    )

    patterns = [
        # "January 5, 2025" / "Jan 5 2025" / "Jan. 5, 2025"
        rf"{MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}",
        # "5 January 2025" / "5th Jan 2025"
        rf"\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}\.?\s+\d{{4}}",
        # "Friday, January 5, 2025"
        rf"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+{MONTHS}\.?\s+\d{{1,2}},?\s+\d{{4}}",
        # "01/05/2025" or "01-05-2025" or "1/5/25"
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
        # ISO 8601: "2025-01-05"
        r"\b\d{4}-\d{2}-\d{2}\b",
        # "January 5" (no year — year inferred downstream)
        rf"{MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?",
        # "5th January" / "5 Jan"
        rf"\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            logger.debug("Date extracted: %s", result)
            return result

    logger.debug("No date found in text.")
    return None


def _extract_time(text: str) -> Optional[str]:
    """
    Extract the first recognisable event start time from OCR text.

    Patterns covered:
        - "7:30 PM" / "7:30PM" / "07:30 pm"
        - "7 PM"    / "7PM"
        - "19:30"   (24-hour, no am/pm)
        - "7.30pm"  (period separator — common in UK/AU flyers)
        - Time ranges: "7:00 PM – 9:00 PM" (returns the start time only)

    Args:
        text: Raw OCR text.

    Returns:
        Matched time string as found in the text, or None.
    """
    patterns = [
        # "7:30 PM" / "07:30PM" / "7:30 pm"
        r"\b\d{1,2}:\d{2}\s*[AaPp][Mm]\b",
        # "7.30pm" / "7.30 PM"
        r"\b\d{1,2}\.\d{2}\s*[AaPp][Mm]\b",
        # "7 PM" / "7PM"
        r"\b\d{1,2}\s*[AaPp][Mm]\b",
        # 24-hour: "19:30" / "08:00"
        r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            logger.debug("Time extracted: %s", result)
            return result

    logger.debug("No time found in text.")
    return None


def _extract_phone(text: str) -> Optional[str]:
    """
    Extract a contact phone number from OCR text.

    Patterns covered:
        - E.164 international: "+1-800-555-0199", "+91 98765 43210"
        - US format:           "(555) 867-5309", "555-867-5309"
        - Plain digits:        "9876543210"  (10-digit)
        - With extensions:     "555-1234 ext. 42"
        - India mobile:        "+91-9999999999"

    Args:
        text: Raw OCR text.

    Returns:
        Best-matched phone string, or None.
    """
    patterns = [
        # International with country code: "+1 (800) 555-0199" / "+91-98765-43210"
        r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,5}[\s\-]?\d{4,6}",
        # US/Canada: "(555) 867-5309" / "555-867-5309" / "555.867.5309"
        r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?:\s*(?:ext|x)\.?\s*\d{1,5})?",
        # Plain 10-digit: "9876543210"
        r"\b\d{10}\b",
        # 7-digit local: "867-5309"
        r"\b\d{3}[\s.\-]\d{4}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            logger.debug("Phone extracted: %s", result)
            return result

    logger.debug("No phone number found in text.")
    return None


def _extract_website(text: str) -> Optional[str]:
    """
    Extract the first URL from OCR text.

    Patterns covered:
        - Full URL:    "https://www.example.com/events"
        - HTTP:        "http://example.com"
        - No scheme:   "www.example.com"
        - Common TLDs: .com, .org, .net, .io, .co, .edu, .gov, .in, .uk

    Args:
        text: Raw OCR text.

    Returns:
        First matched URL string, or None.
    """
    patterns = [
        # Full URL with scheme (http/https)
        r"https?://(?:www\.)?[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+",
        # www. prefix without scheme
        r"www\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:[/\w\-.~?=%&]*)?",
        # Bare domain with common TLDs
        r"\b[a-zA-Z0-9\-]+\.(?:com|org|net|io|co|edu|gov|in|uk|event)(?:/[^\s]*)?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(0).strip().rstrip(".,;)")
            logger.debug("Website extracted: %s", result)
            return result

    logger.debug("No website URL found in text.")
    return None


def _extract_location(text: str) -> Optional[str]:
    """
    Detect venue/location using spaCy Named Entity Recognition.

    Entity labels used:
        GPE  — Countries, cities, states (e.g. "New York", "Mumbai")
        LOC  — Non-GPE locations (e.g. "Central Park", "Riverside Hall")
        FAC  — Facilities (e.g. "Madison Square Garden", "Convention Center")

    Fallback (when spaCy unavailable or returns nothing):
        Regex for common address patterns:
        - "at The Grand Hall"
        - "123 Main Street, City"
        - "Venue:" or "Location:" prefix

    Args:
        text: Raw OCR text.

    Returns:
        Best location string found, or None.
    """
    # Primary: spaCy NER
    if nlp is not None:
        doc = nlp(text[:5000])   # Cap at 5000 chars for efficiency
        location_labels = {"GPE", "LOC", "FAC"}
        locations = [
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ in location_labels and len(ent.text.strip()) > 2
        ]
        if locations:
            # Prefer FAC (facility names) and LOC over generic GPE city names
            result = locations[0]
            logger.debug("Location (spaCy NER): %s", result)
            return result

    # Fallback: Regex for "at <Place>", "Venue: <Place>", or address lines
    fallback_patterns = [
        # "Venue: Grand Convention Center" / "Location: ..."
        r"(?:venue|location|held at|at|place)[:\s]+([A-Z][^\n,]{3,60})",
        # Address: "123 Main Street, Springfield"
        r"\b\d{1,5}\s+[A-Z][a-zA-Z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Blvd|Drive|Dr|Lane|Ln|Hall|Center|Centre|Park|Ground|Complex)\b",
    ]

    for pattern in fallback_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = (match.group(1) if match.lastindex else match.group(0)).strip()
            logger.debug("Location (regex fallback): %s", result)
            return result

    logger.debug("No location found in text.")
    return None


def _extract_organization(text: str) -> Optional[str]:
    """
    Detect the event organizer using spaCy Named Entity Recognition.

    Entity labels used:
        ORG  — Companies, agencies, institutions
               (e.g. "Google", "City Council", "Jazz Festival Committee")

    Fallback (when spaCy unavailable or returns nothing):
        - Regex for "Organized by:", "Presented by:", "Hosted by:" prefixes
        - First all-caps or title-case line heuristic (common on flyers)

    Args:
        text: Raw OCR text.

    Returns:
        Best organizer string found, or None.
    """
    # Primary: spaCy NER
    if nlp is not None:
        doc = nlp(text[:5000])
        orgs = [
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ == "ORG" and len(ent.text.strip()) > 2
        ]
        if orgs:
            result = orgs[0]
            logger.debug("Organization (spaCy NER): %s", result)
            return result

    # Fallback: explicitly labelled organizer lines
    labelled_patterns = [
        r"(?:organized by|presented by|hosted by|brought to you by|sponsor)[:\s]+([^\n]{3,80})",
        r"(?:organizer|organiser|host)[:\s]+([^\n]{3,80})",
    ]

    for pattern in labelled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(1).strip()
            logger.debug("Organization (regex fallback): %s", result)
            return result

    # Last-resort: first all-caps token line (e.g. "ANNUAL JAZZ FESTIVAL")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped.isupper() and 3 < len(stripped) < 80:
            logger.debug("Organization (all-caps heuristic): %s", stripped)
            return stripped.title()   # Normalise casing

    logger.debug("No organization found in text.")
    return None


def _classify_category(text: str) -> Optional[str]:
    """
    Classify the event into a category using keyword matching.

    Categories and their keyword triggers:
        Concert/Music   : music, concert, band, dj, live, festival, gig
        Sports          : tournament, match, game, league, race, marathon, championship
        Workshop        : workshop, training, seminar, class, bootcamp, course, learn
        Conference      : conference, summit, symposium, forum, convention
        Exhibition      : exhibition, expo, gallery, show, showcase, display
        Food & Drink    : food, cuisine, tasting, dinner, brunch, feast, bar
        Networking      : networking, meetup, mixer, social, connect
        Fundraiser      : charity, fundraiser, donation, benefit, raffle, auction
        Cultural        : cultural, dance, art, theatre, theater, comedy, film, cinema
        Religious       : church, prayer, worship, mass, congregation, religious

    Args:
        text: Raw OCR text (case-insensitive matching).

    Returns:
        Category string, or None if no keywords matched.
    """
    CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "Concert / Music"   : ["music", "concert", "band", "dj", "live", "festival", "gig", "performance", "singer"],
        "Sports"            : ["tournament", "match", "game", "league", "race", "marathon", "championship", "sports", "cup"],
        "Workshop"          : ["workshop", "training", "seminar", "class", "bootcamp", "course", "learn", "skill"],
        "Conference"        : ["conference", "summit", "symposium", "forum", "convention", "keynote", "panel"],
        "Exhibition"        : ["exhibition", "expo", "gallery", "show", "showcase", "display", "fair"],
        "Food & Drink"      : ["food", "cuisine", "tasting", "dinner", "brunch", "feast", "bar", "chef", "culinary"],
        "Networking"        : ["networking", "meetup", "mixer", "social", "connect", "community"],
        "Fundraiser"        : ["charity", "fundraiser", "donation", "benefit", "raffle", "auction", "gala"],
        "Cultural"          : ["cultural", "dance", "art", "theatre", "theater", "comedy", "film", "cinema", "heritage"],
        "Religious"         : ["church", "prayer", "worship", "mass", "congregation", "religious", "spiritual"],
    }

    text_lower = text.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                logger.debug("Category matched: %s (keyword: %s)", category, keyword)
                return category

    logger.debug("No category keywords matched.")
    return None

