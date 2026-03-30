from prefect import flow, task, get_run_logger

# Import your template modules
from glue_job.job_script import main as run_glue_template
from lambda.lambda_function import lambda_handler as run_lambda_template

# Optional: Import repo utilities
from scripts.deploy_blocks import deploy_blocks
from scripts.register_flows import register_flows


# -----------------------------------------------------
# PIPELINE TASKS
# -----------------------------------------------------

@task(retries=2)
def extract():
    logger = get_run_logger()
    logger.info("Extracting raw data...")
    return {"sample": 123}


@task
def transform(data):
    logger = get_run_logger()
    logger.info("Transforming data...")
    return data


@task
def load_to_s3(data):
    logger = get_run_logger()
    logger.info("Loading transformed data to S3...")
    # In a real pipeline, write to S3 here
    return "s3://template-bucket/data/sample.json"


@task
def trigger_glue_job(s3_path):
    logger = get_run_logger()
    logger.info(f"Triggering Glue job using input: {s3_path}")

    # Calls your template Glue job script from glue-job/job_script.py
    glue_result = run_glue_template()
    logger.info(f"Glue job complete: {glue_result}")

    return glue_result


@task
def invoke_lambda(glue_result):
    logger = get_run_logger()
    logger.info(f"Invoking Lambda using Glue result: {glue_result}")

    # Calls your template Lambda script from lambda/lambda_function.py
    lambda_response = run_lambda_template(
        {"glue_output": glue_result},
        None
    )
    logger.info(f"Lambda response: {lambda_response}")

    return lambda_response


@task
def load_to_redshift(lambda_output):
    logger = get_run_logger()
    logger.info("Loading final data into Redshift...")
    return True


# -----------------------------------------------------
# FULL PREFECT FLOW
# -----------------------------------------------------
@flow(name="full-aws-pipeline")
def full_pipeline():
    logger = get_run_logger()
    logger.info("Starting full AWS pipeline...")

    raw = extract()
    transformed = transform(raw)
    s3_output = load_to_s3(transformed)

    glue_output = trigger_glue_job(s3_output)
    lambda_output = invoke_lambda(glue_output)

    load_to_redshift(lambda_output)

    logger.info("Pipeline complete.")


# -----------------------------------------------------
# LOCAL EXECUTION
# -----------------------------------------------------
if __name__ == "__main__":
    full_pipeline()
