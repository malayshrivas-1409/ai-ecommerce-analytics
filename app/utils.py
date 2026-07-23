from datetime import datetime


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def current_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()
