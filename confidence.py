"""
confidence.py
-------------
Deterministic Confidence Scorer for Vision2Schedule — Phase 3.

Responsibilities:
- Calculate a quality score (90–100%) for an extracted event.
- Award points based on the presence of key fields.
"""

def calculate_confidence(event_data: dict) -> float:
    """
    Calculate confidence score based on extracted fields.
    Base score is 90. Each non-empty field adds ~1.43 to the score.
    Capped at 100.0.

    Args:
        event_data: Dictionary of extracted event fields.

    Returns:
        float: Score between 90.0 and 100.0.
    """
    score = 90.0
    fields_to_check = [
        "title", "date", "time", "venue", 
        "organizer", "contact", "website"
    ]
    
    # Increment for each detected field
    increment = 10.0 / len(fields_to_check)
    
    for field in fields_to_check:
        if event_data.get(field):
            score += increment
            
    # Final cleanup: cap at 100.0 and round
    return min(float(round(score, 2)), 100.0)

