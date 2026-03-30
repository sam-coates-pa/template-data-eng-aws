import json
import logging
from unittest.mock import patch
from types import SimpleNamespace

# Import the Lambda function you want to test
from lambda_function import lambda_handler

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TEST] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Fake AWS Context Object
# -----------------------------------------------------
def fake_lambda_context():
    """
    Builds a fake Lambda context object for local testing.
    """
    return SimpleNamespace(
        function_name="local-test-lambda",
        function_version="$LATEST",
        invoked_function_arn="arn:aws:lambda:local:0:function:test",
        memory_limit_in_mb=256,
        aws_request_id="local-test-req-123",
        log_group_name="/aws/lambda/local-test",
        log_stream_name="local-test-stream"
    )


# -----------------------------------------------------
# Optional Mock for boto3 (if Lambda uses AWS services)
# -----------------------------------------------------
def mock_boto3_client(service_name):
    class FakeS3:
        def put_object(self, Bucket, Key, Body, **kwargs):
            logger.info(f"[MOCK] S3 put_object → s3://{Bucket}/{Key}")
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    class FakeLambda:
        def invoke(self, **kwargs):
            logger.info("[MOCK] Lambda invoke called.")
            return {"StatusCode": 200}

    if service_name == "s3":
        return FakeS3()
    if service_name == "lambda":
        return FakeLambda()

    raise NotImplementedError(f"No mock for AWS service: {service_name}")


# -----------------------------------------------------
# Run Lambda locally
# -----------------------------------------------------
def run_lambda_locally(event: dict):
    """
    Executes the Lambda handler locally with an optional mock for boto3.

    :param event: JSON payload that simulates AWS triggers
    :return: Lambda handler response
    """

    logger.info(f"Running Lambda locally with event: {event}")

    with patch("boto3.client", mock_boto3_client):

        context = fake_lambda_context()
        response = lambda_handler(event, context)

        logger.info(f"Lambda completed with response: {json.dumps(response, indent=2)}")
        return response


# -----------------------------------------------------
# Local Test Runner
# -----------------------------------------------------
if __name__ == "__main__":

    test_event = {
        "action": "test",
        "input_data": {"value": 123}
    }

    result = run_lambda_locally(test_event)
    print(json.dumps(result, indent=2))
