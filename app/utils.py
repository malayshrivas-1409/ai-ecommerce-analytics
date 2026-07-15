from datetime import datetime


def get_timestamp():
    """
    Returns current UTC timestamp.
    """
    return datetime.utcnow().isoformat()