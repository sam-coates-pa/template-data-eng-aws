import boto3
import json
import logging
from botocore.exceptions import ClientError

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------
# Lambda Client
# -----------------------------------------------------
lambda_client = boto3.client("lambda")


# -----------------------------------------------------
# Invoke Lambda Function
# -----------------------------------------------------
def invoke_lambda(
    function_name: str,
    payload: dict = None,
    invocation_type: str = "RequestResponse"
) -> dict:
    """
    Invokes an AWS Lambda function programmatically.

    :param function_name: Name or ARN of the Lambda function
    :param payload: JSON dict to pass to Lambda
    :param invocation_type:
        "RequestResponse"  = synchronous (wait for response)
        "Event"            = asynchronous (fire-and-forget)
    :return: Response dict with status, request ID, and optional returned payload
    """

    logger.info(f"Invoking Lambda: {function_name} (type={invocation_type})")

    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload or {}),
        )

        request_id = response.get("ResponseMetadata", {}).get("RequestId")

        result = {
            "lambda_function": function_name,
            "request_id": request_id,
            "status_code": response.get("StatusCode")
        }

        # Synchronous invocation returns a payload
        if invocation_type == "RequestResponse":
            response_payload = response.get("Payload").read()
            try:
                result["response"] = json.loads(response_payload)
            except json.JSONDecodeError:
                result["response"] = response_payload.decode("utf-8")

        logger.info(f"Lambda invocation result: {json.dumps(result, indent=2)}")
        return result

    except ClientError as e:
        logger.error(f"Error invoking Lambda: {e}")
        raise


# -----------------------------------------------------
# Local Test
# -----------------------------------------------------
if __name__ == "__main__":
    FUNCTION_NAME = "my-lambda-template"

    PAYLOAD = {
        "action": "test",
        "input": "sample"
    }

    output = invoke_lambda(FUNCTION_NAME, PAYLOAD)
    print(output)

