
from prefect import flow, task

@task
def extract():
    return {"sample": 123}

@task
def transform(data):
    return data

@task
def load_to_s3(data):
    return True

@task
def trigger_glue_job():
    return True

@task
def invoke_lambda():
    return True

@task
def load_to_redshift():
    return True

@flow(name="full-aws-pipeline")
def full_pipeline():
    d = extract()
    t = transform(d)
    load_to_s3(t)
    trigger_glue_job()
    invoke_lambda()
    load_to_redshift()

if __name__ == '__main__':
    full_pipeline()
