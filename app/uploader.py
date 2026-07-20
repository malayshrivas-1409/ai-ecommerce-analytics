import os
import time
import boto3

from app.config import (
    BUCKET_NAME,
    RAW_PREFIX,
    UPLOAD_RETRY_COUNT,
    UPLOAD_RETRY_DELAY
)

s3 = boto3.client("s3")


def get_s3_prefix(filename):
    """
    Determine the correct S3 raw folder
    based on the generated filename.
    """

    if filename.startswith("orders_"):
        return f"{RAW_PREFIX}orders/"

    elif filename.startswith("clicks_"):
        return f"{RAW_PREFIX}clicks/"

    elif filename.startswith("carts_"):
        return f"{RAW_PREFIX}carts/"

    else:
        raise ValueError(
            f"Unknown file type: {filename}"
        )


def upload_file(file_path):

    if not os.path.exists(file_path):
        return False

    filename = os.path.basename(file_path)

    try:
        s3_prefix = get_s3_prefix(filename)

    except ValueError as e:
        print(e)
        return False

    s3_key = f"{s3_prefix}{filename}"

    for attempt in range(UPLOAD_RETRY_COUNT):

        try:

            s3.upload_file(
                file_path,
                BUCKET_NAME,
                s3_key
            )

            print(
                f"{filename} uploaded successfully "
                f"to s3://{BUCKET_NAME}/{s3_key}"
            )

            return True

        except Exception as e:

            print(
                f"Upload Attempt {attempt + 1} Failed "
                f"for {filename}"
            )

            print(e)

            time.sleep(UPLOAD_RETRY_DELAY)

    return False