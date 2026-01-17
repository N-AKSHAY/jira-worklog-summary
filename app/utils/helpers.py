def format_seconds(seconds: int) -> str:
    """Formats seconds into a human-readable string (e.g., '2h 30m')."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours and minutes:
        return f"{hours}h {minutes}m"
    elif hours:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def extract_comment(comment_obj) -> str:
    """Extracts text from a Jira comment object."""
    if not comment_obj:
        return ""

    texts = []
    for block in comment_obj.get("content", []):
        for item in block.get("content", []):
            if item.get("type") == "text":
                texts.append(item.get("text", ""))
    return " ".join(texts)
