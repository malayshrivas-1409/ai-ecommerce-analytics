# AWS Configuration

BUCKET_NAME = "your-s3-bucket-name"

# S3 folder
RAW_PREFIX = "raw/orders/"

# Local log folder
LOG_DIRECTORY = "../logs"

# Log file name
LOG_FILE = "ecommerce_events.log"

MAX_EVENTS_PER_FILE = 10

UPLOAD_RETRY_COUNT = 3

UPLOAD_RETRY_DELAY = 5