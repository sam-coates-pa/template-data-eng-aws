import logging
from unittest.mock import patch, MagicMock
import json

# Import your real loader module
from loader import load_to_redshift, copy_to_redshift

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TEST] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Fake Redshift Connection + Cursor
# -----------------------------------------------------
class FakeCursor:
    def execute(self, sql, params=None):
        logger.info("[MOCK] Executing SQL:")
        logger.info(f"SQL: {sql}")
        logger.info(f"Params: {params}")

    def close(self):
        logger.info("[MOCK] Closing cursor.")


class FakeConnection:
    autocommit = True

    def cursor(self):
        logger.info("[MOCK] Creating cursor.")
        return FakeCursor()

    def close(self):
        logger.info("[MOCK] Closing Redshift connection.")


# -----------------------------------------------------
# Test COPY Command
# -----------------------------------------------------
def test_copy_to_redshift():
    fake_conn = FakeConnection()

    logger.info("Running COPY test...")

    with patch("loader.psycopg2.connect", return_value=fake_conn):

        # Run COPY using loader implementation
        copy_to_redshift(
            conn=fake_conn,
            table="test_table",
            s3_path="s3://test-bucket/raw/data.json",
            iam_role_arn="arn:aws:iam::123456789012:role/TestRole",
            region="eu-west-2",
            format="JSON",
            jsonpath="auto"
        )

    logger.info("COPY command test completed.")


# -----------------------------------------------------
# Test Full Redshift Loader
# -----------------------------------------------------
def test_full_loader():
    """
    Runs load_to_redshift end-to-end with fake connections.
    """

    logger.info("Running full Redshift load test...")

    with patch("loader.psycopg2.connect", return_value=FakeConnection()):

        result = load_to_redshift(
            host="fake",
            port=5439,
            db="testdb",
            user="test",
            password="test",
            table="test_table",
            s3_path="s3://test-bucket/raw/data.json",
            iam_role_arn="arn:aws:iam::123456789012:role/TestRole"
        )

    logger.info("Test finished with result:")
    logger.info(json.dumps(result, indent=2))

    return result


# -----------------------------------------------------
# Local Test Runner
# -----------------------------------------------------
if __name__ == "__main__":
    logger.info("--- Running Redshift COPY Unit Test ---")
    test_copy_to_redshift()

    logger.info("--- Running Full Loader Unit Test ---")
    output = test_full_loader()
    print(json.dumps(output, indent=2))
