
"""
Deploy Prefect blocks for AWS template.
This is a stub that users can extend.
"""
from prefect_aws import AwsCredentials
from prefect import flow

def create_blocks():
    # Example: Create AWS Credentials block
    creds = AwsCredentials(
        aws_access_key_id="YOUR_KEY",  # replace with env var loading
        aws_secret_access_key="YOUR_SECRET"
    )
    creds.save("aws-creds", overwrite=True)
    print("AWS Credentials block deployed.")

if __name__ == "__main__":
    create_blocks()
