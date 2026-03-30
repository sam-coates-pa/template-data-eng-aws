import boto3
import time
import json
import logging
from botocore.exceptions import ClientError

# -----------------------------------------------------
# Logging Setup
# -----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------
# Glue Client
# -----------------------------------------------------
glue = boto3.client("glue")


# -----------------------------------------------------
# Start the Glue Job
# -----------------------------------------------------
def start_glue_job(job_name: str, params: dict = None) -> str:
    """
    Triggers an AWS Glue job and returns the run ID.

    :param job_name: Name of the Glue job
    :param params: Optional dict of job parameters
    :return: JobRunId string
    """

    try:
        logger.info(f"Starting Glue job: {job_name}...")
        response = glue.start_job_run(
            JobName=job_name,
            Arguments=params or {}
        )

        job_run_id = response["JobRunId"]
        logger.info(f"Glue job started successfully: Run ID = {job_run_id}")
        return job_run_id

    except ClientError as e:
        logger.error(f"Failed to start Glue job: {e}")
        raise


# -----------------------------------------------------
# Poll Glue Job Status
# -----------------------------------------------------
def wait_for_completion(job_name: str, job_run_id: str, delay=10) -> str:
    """
    Polls Glue job until it completes.

    :param job_name: Glue job name
    :param job_run_id: Run ID returned from start_glue_job()
    :param delay: Poll interval in seconds
    :return: Final job state: SUCCEEDED / FAILED / STOPPED / TIMEOUT
    """

    logger.info(f"Monitoring Glue job: {job_name}, Run ID: {job_run_id}")

    while True:
        response = glue.get_job_run(
            JobName=job_name,
            RunId=job_run_id,
            PredecessorsIncluded=False
        )

        state = response["JobRun"]["JobRunState"]
        logger.info(f"Glue job status: {state}")

        if state in ("SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"):
            return state

        time.sleep(delay)


# -----------------------------------------------------
# Combined Helper (Start + Wait)
# -----------------------------------------------------
def trigger_glue_job(job_name: str, params: dict = None) -> dict:
    """
    Orchestrates running a Glue job from start to finish.
    Returns structured response with run ID and status.
    """

    job_run_id = start_glue_job(job_name, params)
    final_status = wait_for_completion(job_name, job_run_id)

    result = {
        "job_name": job_name,
        "job_run_id": job_run_id,
        "final_status": final_status
    }

    logger.info(f"Glue job completed: {json.dumps(result, indent=2)}")
    return result


# -----------------------------------------------------
# Local Testing
# -----------------------------------------------------
if __name__ == "__main__":
    JOB_NAME = "my_glue_job_template"

    PARAMS = {
        "--input_path": "s3://my-bucket/raw/",
        "--output_path": "s3://my-bucket/processed/"
    }

    output = trigger_glue_job(JOB_NAME, PARAMS)
    print(output)
