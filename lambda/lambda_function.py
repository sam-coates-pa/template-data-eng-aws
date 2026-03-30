
import json
import boto3
import logging
import os
from datetime import datetime

# -----------------------------------------------------
# Logging Configuration
# -----------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# -----------------------------------------------------
# Optional AWS Clients
# -----------------------------------------------------
s3_client = boto3.client("s3")

# -----------------------------------------------------
# Environment Variables (editable by anyone)
# -----------------------------------------------------
OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "my-output-bucket")
OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "lambda-output/")

# -----------------------------------------------------
# Helper Function: Write to S3
# -----------------------------------------------------
def write_to_s3(data, bucket, prefix):
    key = f"{prefix}output_{datetime.utcnow().isoformat()}.json"
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    logger.info(f"Successfully wrote output to s3://{bucket}/{key}")
    return key

# -----------------------------------------------------
# Transformation Logic (TEMPLATE)
# -----------------------------------------------------
def process_event(event):
    """
    Place all transformation, business rules, or enrichment logic here.
    Modify this function freely for your specific use case.
    """

    logger.info("Running transformation logic...")

    # Example transformation (safe to delete)
    processed = {
        "originalEvent": event,
        "processedAt": datetime.utcnow().isoformat(),
        "status": "success"
    }

    return processed

# -----------------------------------------------------
# Main Lambda Handler
# -----------------------------------------------------
def lambda_handler(event, context):
    """
    Entry point for AWS Lambda.
    Supports:
    - API Gateway events
    - S3 events
    - EventBridge
    - Generic triggers
    """

    logger.info("Lambda function started.")
    logger.info(f"Incoming event: {json.dumps(event)}")

    try:
        # --- Step 1: Process event ---
        result = process_event(event)

        # --- Step 2: Write optional output to S3 ---
        s3_key = write_to_s3(result, OUTPUT_BUCKET, OUTPUT_PREFIX)

        # --- Step 3: Prepare response ---
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Lambda executed successfully.",
                "s3Location": f"s3://{OUTPUT_BUCKET}/{s3_key}"
            })
        }

        logger.info("Lambda completed successfully.")
        return response

    except Exception as e:
        logger.error(f"Error processing Lambda: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
