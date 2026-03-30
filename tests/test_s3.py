import json
import logging
from unittest.mock import patch

# Import the uploader functions
from uploader import (
    upload_file_to_s3,
    upload_json_to_s3,
    upload_bytes_to_s3
)

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TEST] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Fake S3 Client for Local Testing
# -----------------------------------------------------
class FakeS3Client:
    """
    A simple mock S3 client to simulate uploads without touching AWS.
    """

    def upload_file(self, Filename, Bucket, Key):
        logger.info(f"[MOCK] upload_file → {Filename} → s3://{Bucket}/{Key}")
        return True

    def put_object(self, Bucket, Key, Body, **kwargs):
        logger.info(f"[MOCK] put_object → s3://{Bucket}/{Key}")
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def mock_boto3_client(service_name):
    if service_name == "s3":
        return FakeS3Client()
    raise NotImplementedError(f"No mock client for: {service_name}")


# -----------------------------------------------------
# Test File Upload
# -----------------------------------------------------
def test_upload_file():
    logger.info("Running file upload test...")

    with patch("uploader.s3", FakeS3Client()):
        result = upload_file_to_s3(
            local_path="tests/sample.txt",
            bucket="test-bucket",
            key="raw/sample.txt"
        )

    logger.info(f"Result: {json.dumps(result, indent=2)}")
    return result


# -----------------------------------------------------
# Test JSON Upload
# -----------------------------------------------------
def test_upload_json():
    logger.info("Running JSON upload test...")

    with patch("uploader.s3", FakeS3Client()):
        result = upload_json_to_s3(
            data={"hello": "world"},
            bucket="test-bucket",
            key="json/sample.json"
        )

    logger.info(f"Result: {json.dumps(result, indent=2)}")
    return result


# -----------------------------------------------------
# Test Bytes Upload
# -----------------------------------------------------
def test_upload_bytes():
    logger.info("Running bytes upload test...")

    with patch("uploader.s3", FakeS3Client()):
        result = upload_bytes_to_s3(
            bytes_data=b"binarydata",
            bucket="test-bucket",
            key="binary/sample.bin"
        )

    logger.info(f"Result: {json.dumps(result, indent=2)}")
    return result


# -----------------------------------------------------
# Local Test Runner
# -----------------------------------------------------
if __name__ == "__main__":
    logger.info("--- S3 File Upload Test ---")
    print(json.dumps(test_upload_file(), indent=2))

    logger.info("--- S3 JSON Upload Test ---")
    print(json.dumps(test_upload_json(), indent=2))

    logger.info("--- S3 Bytes Upload Test ---")
    print(json.dumps(test_upload_bytes(), indent=2))

