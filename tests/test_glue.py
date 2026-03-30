import sys
import json
import logging
from unittest.mock import patch

# Adjust this import to match your real Glue job script
from job_script import main as glue_main

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TEST] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Fake AWS Glue Runtime Environment
# -----------------------------------------------------
class FakeGlueContext:
    """Simple mock of GlueContext used for local testing."""

    def __init__(self):
        self.spark_session = None

    def create_dynamic_frame_from_options(self, connection_type, format_options, **kwargs):
        logger.info(f"Simulated read: {connection_type}, options={format_options}")
        return {"test": "dynamic_frame"}


# -----------------------------------------------------
# Fake Job Handler
# -----------------------------------------------------
class FakeGlueJob:
    """Mock for the Glue Job() object."""
    def init(self, name, args):
        logger.info(f"Simulated Glue job init: {name}, args={args}")

    def commit(self):
        logger.info("Simulated Glue job commit.")


# -----------------------------------------------------
# Mock boto3 (optional) if Glue script interacts with S3
# -----------------------------------------------------
def mock_boto3_client(service_name):
    class FakeS3:
        def get_object(self, Bucket, Key):
            logger.info(f"Mock S3 get_object: s3://{Bucket}/{Key}")
            return {"Body": b"{}"}

        def put_object(self, Bucket, Key, Body):
            logger.info(f"Mock S3 put_object: s3://{Bucket}/{Key}")
            return True

    if service_name == "s3":
        return FakeS3()
    raise NotImplementedError(f"No mock for {service_name}")


# -----------------------------------------------------
# Simulate command-line args that Glue normally injects
# -----------------------------------------------------
def simulated_sys_argv(params: dict):
    """
    Builds sys.argv exactly how AWS Glue would.
    """
    argv = ["job_script.py"]  # first element = script name
    for key, val in params.items():
        argv.append(f"--{key}")
        argv.append(val)
    return argv


# -----------------------------------------------------
# Run Glue Job Locally
# -----------------------------------------------------
def run_glue_locally(glue_params: dict):
    """
    Execute Glue job inside a simulated environment.
    Useful for unit tests or CI/CD safety checks.
    """

    logger.info("Preparing simulated Glue environment...")

    # Patch sys.argv to mimic AWS Glue
    test_argv = simulated_sys_argv(glue_params)
    logger.info(f"Simulated sys.argv = {test_argv}")

    with patch.object(sys, "argv", test_argv):
        with patch("job_script.GlueContext", FakeGlueContext):
            with patch("job_script.Job", FakeGlueJob):
                with patch("boto3.client", mock_boto3_client):

                    logger.info("Starting Glue job test run...")
                    result = glue_main()
                    logger.info(f"Glue job finished with result: {result}")

    return result


# -----------------------------------------------------
# Local Test — manually run this script
# -----------------------------------------------------
if __name__ == "__main__":

    # Your test parameters (modify as needed)
    test_params = {
        "input_path": "s3://test-bucket/raw/input.json",
        "output_path": "s3://test-bucket/processed/output.json",
        "run_id": "local-test-001"
    }

    result = run_glue_locally(test_params)
    print(json.dumps({"test_result": result}, indent=2))
