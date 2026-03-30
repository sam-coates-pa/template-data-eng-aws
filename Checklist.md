# ✅ AWS Template Repository — Setup Checklist

Welcome! This checklist ensures you correctly configure your environment after cloning this AWS Data Engineering Template.

---

## 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd template-data-eng-aws
```
## 2️⃣ Create Your .env File
Copy the template:
Shellcp env.example .envShow more lines
Fill out the values in .env:
Required AWS Variables
```bash
 AWS_ACCESS_KEY_ID
 AWS_SECRET_ACCESS_KEY
 AWS_REGION
```
### S3
```bash
 S3_BUCKET_NAME
 S3_PREFIX
```
### AWS Glue
```bash
 GLUE_JOB_NAME
 GLUE_TEMP_DIR
```
### Lambda
```bash
 LAMBDA_FUNCTION_NAME
```
### Redshift
```bash
 REDSHIFT_CLUSTER_ID
 REDSHIFT_DATABASE
 REDSHIFT_DB_USER
 REDSHIFT_IAM_ROLE_ARN
```
### Optional
```bash
 AWS_SESSION_TOKEN
 PREFECT_API_URL
 PREFECT_API_KEY
```

## 3️⃣ Configure AWS CLI (if running locally)
Shellaws configureShow more lines
Verify:

 The CLI profile matches your credentials
 Run aws sts get-caller-identity to ensure permissions exist


## 4️⃣ Ensure AWS Resources Exist
### S3

 - Bucket exists
 - Prefix structure is correct

### Glue

 - Glue job exists
 - IAM role has S3 + CloudWatch permissions

### Lambda

 - Lambda function exists
 - Execution role is configured correctly

### Redshift

 - Cluster reachable
 - COPY IAM role attached
 - Networking/VPC configured


## 5️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
## 6️⃣ Run Local Test Scripts (recommended)
```bash
 python s3/test_s3_uploader.py
 python glue-job/test_glue_job.py
 python lambda/test_lambda_function.py
 python redshift/test_redshift_loader.py
```

## 7️⃣ Run the Full Prefect Pipeline
```bash
python flows/full_pipeline.py
```
## 8️⃣ (Optional) Prefect Deployment
```bash
prefect deployment build flows/full_pipeline.py:full_pipeline --name aws-p
```
