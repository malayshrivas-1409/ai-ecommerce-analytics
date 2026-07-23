import os
import time

import boto3

from app.config import BUCKET_NAME, RAW_PREFIX, UPLOAD_RETRY_COUNT, UPLOAD_RETRY_DELAY
from app.logger import logger


# ============================================================================
# AWS S3 CLIENT
# ============================================================================

s3 = boto3.client("s3")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_s3_prefix(filename: str) -> str:
    """Determine the correct S3 prefix based on filename"""

    if filename.startswith("orders_"):
        return f"{RAW_PREFIX}orders/"
    elif filename.startswith("clicks_"):
        return f"{RAW_PREFIX}clicks/"
    elif filename.startswith("carts_"):
        return f"{RAW_PREFIX}carts/"
    else:
        raise ValueError(f"Unknown file type: {filename}")


# ============================================================================
# FILE UPLOAD
# ============================================================================

def upload_file(file_path: str) -> bool:
    """
    Upload file to S3 with retry logic

    Args:
        file_path: Local file path to upload

    Returns:
        True if upload successful, False otherwise
    """

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    filename = os.path.basename(file_path)

    try:
        s3_prefix = get_s3_prefix(filename)
    except ValueError as e:
        logger.error(str(e))
        return False

    s3_key = f"{s3_prefix}{filename}"

    for attempt in range(UPLOAD_RETRY_COUNT):
        try:
            s3.upload_file(file_path, BUCKET_NAME, s3_key)

            logger.info(
                f"{filename} uploaded successfully to s3://{BUCKET_NAME}/{s3_key}"
            )

            return True

        except Exception as e:
            logger.warning(
                f"Upload Attempt {attempt + 1}/{UPLOAD_RETRY_COUNT} failed for {filename}: {e}"
            )

            if attempt < UPLOAD_RETRY_COUNT - 1:
                time.sleep(UPLOAD_RETRY_DELAY)

    logger.error(f"Failed to upload {filename} after {UPLOAD_RETRY_COUNT} attempts")

    return False
