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


def upload_file(file_path):

    if not os.path.exists(file_path):
        return False

    filename = os.path.basename(file_path)

    for _ in range(UPLOAD_RETRY_COUNT):

        try:

            s3.upload_file(
                file_path,
                BUCKET_NAME,
                RAW_PREFIX + filename
            )

            print(f"{filename} uploaded successfully")

            return True

        except Exception as e:

            print(e)

            time.sleep(UPLOAD_RETRY_DELAY)

    return False