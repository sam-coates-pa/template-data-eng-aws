import boto3
import json
import logging
import os
from botocore.exceptions import ClientError

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------
# S3 Client
# -----------------------------------------------------
s3 = boto3.client("s3")


# -----------------------------------------------------
# Upload File to S3
# -----------------------------------------------------
def upload_file_to_s3(local_path: str, bucket: str, key: str) -> dict:
    """
    Uploads a local file to S3.

    :param local_path: Path to the local file
    :param bucket: S3 bucket name
    :param key: S3 object key (path inside bucket)
    :return: Metadata dictionary
    """
    try:
        logger.info(f"Uploading file {local_path} to s3://{bucket}/{key}")

        s3.upload_file(local_path, bucket, key)

        return {
            "bucket": bucket,
            "key": key,
            "status": "SUCCESS",
            "type": "file-upload"
        }

    except ClientError as e:
        logger.error(f"Failed to upload file: {e}")
        raise


# -----------------------------------------------------
# Upload JSON Data to S3
# -----------------------------------------------------
def upload_json_to_s3(data: dict, bucket: str, key: str) -> dict:
    """
    Serializes a Python dict to JSON and uploads to S3.
    """
    try:
        logger.info(f"Uploading JSON object to s3://{bucket}/{key}")

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )

        return {
            "bucket": bucket,
            "key": key,
            "status": "SUCCESS",
            "type": "json-upload"
        }

    except ClientError as e:
        logger.error(f"Failed to upload JSON: {e}")
        raise


# -----------------------------------------------------
# Upload Raw Bytes to S3
# -----------------------------------------------------
def upload_bytes_to_s3(bytes_data: bytes, bucket: str, key: str) -> dict:
    """
    Uploads a bytes payload to S3.
    Useful for binary files, Parquet, images, etc.
    """
    try:
        logger.info(f"Uploading bytes to s3://{bucket}/{key}")

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=bytes_data
        )

        return {
            "bucket": bucket,
            "key": key,
            "status": "SUCCESS",
            "type": "bytes-upload"
        }

    except ClientError as e:
        logger.error(f"Failed to upload bytes: {e}")
        raise


# -----------------------------------------------------
# Local Test
# -----------------------------------------------------
if __name__ == "__main__":
    # Example: Upload JSON
    response = upload_json_to_s3(
        data={"message": "hello world"},
        bucket="my-template-bucket",
        key="tests/sample.json"
    )
    print(response)

