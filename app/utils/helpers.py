"""Utility functions for formatting and data extraction."""

from app.core.constants import SECONDS_PER_HOUR, SECONDS_PER_MINUTE


def format_seconds(seconds: int) -> str:
    """Format seconds into a human-readable string.
    
    Args:
        seconds: Number of seconds to format.
        
    Returns:
        Formatted string (e.g., '2h 30m', '1h', '45m').
        
    Examples:
        >>> format_seconds(9000)
        '2h 30m'
        >>> format_seconds(3600)
        '1h'
        >>> format_seconds(2700)
        '45m'
    """
    hours = seconds // SECONDS_PER_HOUR
    minutes = (seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE

    if hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def extract_comment(comment_obj: dict) -> str:
    """Extract text from a Jira comment object.
    
    Jira comments are stored in a structured format with nested content blocks.
    This function extracts all text content from the comment structure.
    
    Args:
        comment_obj: Jira comment object (dict) with nested content structure.
        
    Returns:
        Extracted text content as a single string, or empty string if no comment.
        
    Example:
        >>> comment = {
        ...     "content": [
        ...         {
        ...             "content": [
        ...                 {"type": "text", "text": "Worked on"},
        ...                 {"type": "text", "text": "feature implementation"}
        ...             ]
        ...         }
        ...     ]
        ... }
        >>> extract_comment(comment)
        'Worked on feature implementation'
    """
    if not comment_obj:
        return ""

    texts = []
    for block in comment_obj.get("content", []):
        for item in block.get("content", []):
            if item.get("type") == "text":
                texts.append(item.get("text", ""))
    return " ".join(texts)
