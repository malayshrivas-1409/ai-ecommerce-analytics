import os


# ============================================================================
# AWS S3 CONFIGURATION
# ============================================================================

BUCKET_NAME = os.getenv(
    "BUCKET_NAME",
    "malay-comm-datalake-2026",
)

RAW_PREFIX = "raw/"


# ============================================================================
# EVENT GENERATION CONFIGURATION
# ============================================================================

LOG_DIRECTORY = "logs"

MAX_EVENTS_PER_FILE = int(
    os.getenv("MAX_EVENTS_PER_FILE", "10")
)


# ============================================================================
# UPLOAD RETRY CONFIGURATION
# ============================================================================

UPLOAD_RETRY_COUNT = 3
UPLOAD_RETRY_DELAY = 5
