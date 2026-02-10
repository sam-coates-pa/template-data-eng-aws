# AWS Data Engineering Template

A practical, production‑minded template for building **AWS‑native data pipelines**. It includes ready‑made patterns for **S3 ingestion**, **Glue ETL**, **Lambda validation**, **Redshift loading**, **Athena SQL use**, **Step Functions for heavy workflows**, and **API Gateway → Lambda ingestion**.

> Use this as a GitHub Template Repository to give teams a fast, consistent starting point.

---

## What's included
- **End‑to‑end flow**: Extract → Stage to S3 → Glue ETL → Lambda validation → Load to Redshift
- **AWS modules**: S3 utilities, Glue job trigger, Lambda invoker, Redshift loader (psycopg2 + Data API)
- **Extras**: Athena query examples, Step Functions pattern, API Gateway → Lambda ingestion pattern
- **Dev experience**: Config files, tests, Makefile, (optional) GitHub Actions for CI and Prefect deployment

---

## Reference Architecture
```
Source/API → (API Gateway → Lambda) → Prefect Flow
                 │                       │
                 └──────────────────────► │ Extract
                                          │
                               S3 (raw) ◄─┘
                                    │
                                    ▼
                              AWS Glue (ETL)
                                    │
                               S3 (processed)
                                    │
                                    ▼
                            Lambda (validation)
                                    │
                                    ▼
                                Redshift (DW)
                                    │
                                    ▼
                              Athena (ad‑hoc)
```

---

## Project Layout (key folders)
```
flows/                      # Prefect flows
src/aws/s3/                 # S3 helpers (read/write, partitions)
src/aws/glue/               # Glue job trigger helpers
src/aws/lambda/             # Lambda invocation helpers
src/aws/redshift/           # Redshift loaders (psycopg2 + Data API)
_glue-job/                  # Glue ETL job script(s)
_lambda/example_lambda/     # Example Lambda function
athena/                     # Athena SQL examples
stepfunctions/              # Sample ASL state machine (JSON/YAML)
api-gateway/                # Example OpenAPI spec + mapping
config/                     # dev/prod config
.tests/                     # unit/integration tests
```

---

## Quick Start
1) **Clone** the repo created from this template.
2) **Configure IAM Roles** for your runtime (EC2/ECS/EKS) with least privilege to S3, Glue, Lambda, Redshift, and (optional) Step Functions.
3) **Install dependencies**:
```bash
pip install -r requirements.txt
```
4) **Run locally** (example flow):
```bash
python flows/full_pipeline.py --run-date 2026-01-01
```
5) **(Optional) Prefect**: Set `PREFECT_API_URL` and `PREFECT_API_KEY` and run deployments:
```bash
prefect deploy --all
```

---

## IAM & Security
- Use **IAM roles** (no long‑lived keys). Separate roles for Glue, Lambda, Redshift access, and the host/runner (EC2/ECS/EKS).
- Apply **least privilege**: fine‑grained S3 prefixes; scoped Glue/Lambda permissions; Redshift data‑api:ExecuteStatement only where needed.
- Enforce **S3 Block Public Access**, default **SSE‑S3 or SSE‑KMS** encryption, and **VPC endpoints** for private connectivity.

---

## Prefect Flow Pattern (simplified)
```python
from prefect import flow, task

@task(retries=3)
def extract(run_date: str) -> dict:
    # fetch from API or source and return payload/manifest
    ...

@task
def stage_to_s3(payload: dict) -> str:
    # write raw JSON/CSV; return S3 URI
    ...

@task
def trigger_glue_job(s3_uri: str) -> str:
    # start glue job with arguments and return job run id
    ...

@task
def invoke_validator(s3_processed_prefix: str) -> None:
    ...

@task
def load_to_redshift(s3_processed_prefix: str) -> int:
    # COPY (driver) or Data API inserts
    ...

@flow(name="full-aws-pipeline")
def pipeline(run_date: str):
    raw_uri = stage_to_s3(extract(run_date))
    processed_prefix = trigger_glue_job(raw_uri)
    invoke_validator(processed_prefix)
    load_to_redshift(processed_prefix)
```

---

## S3 Conventions
- Buckets split by environment: `my‑proj‑raw‑dev`, `my‑proj‑processed‑dev`, etc.
- Prefixes: `raw/<source>/<yyyy>/<mm>/<dd>/...` and `processed/<domain>/<table>/partition=...`
- File formats: **Parquet + Snappy** for analytics; **JSON/CSV** accepted as raw.

---

## Glue ETL (Spark) – Example Job
**Goal:** Convert raw JSON/CSV in S3 → partitioned Parquet in `processed/` with schema enforcement.

Job arguments (example):
```
--job-language python
--job-bookmark-option job-bookmark-enable
--enable-metrics
--enable-continuous-cloudwatch-log
--additional-python-modules pyarrow==14.0.2
--TempDir s3://<bucket>/tmp/glue/
--raw_prefix s3://<raw-bucket>/source/api/2026/01/01/
--out_prefix s3://<processed-bucket>/domain/table/
```

Skeleton (PySpark):
```python
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ["raw_prefix", "out_prefix"])
sc = SparkContext()
glue = GlueContext(sc)
spark = glue.spark_session

raw = spark.read.json(args["raw_prefix"])  # or .csv(...)
# transformations ...
raw.write.mode("append").partitionBy("ingest_date").parquet(args["out_prefix"]) 
```

**Tips**
- Enable **bookmarks** for incremental loads.
- Keep **small files** under control (coalesce/repartition).
- Emit **metrics** to CloudWatch; tag job runs.

---

## Lambda Validator – Pattern
- Input: processed S3 prefix
- Checks: row counts, required columns, basic domain rules
- Outputs: pass/fail; optional SNS/Slack notification
- Keep the function **idempotent** and **< 15 min** runtime; prefer Parquet readers (pyarrow) if needed.

Minimal handler:
```python
def handler(event, context):
    prefix = event["processed_prefix"]
    # perform validations (row counts, schema)
    return {"status": "ok", "prefix": prefix}
```

---

## Redshift Loading – Two Options
1) **Driver (psycopg2)**
   - Use **COPY from S3** for large loads:
   ```sql
   COPY schema.table
   FROM 's3://bucket/processed/domain/table/'
   IAM_ROLE 'arn:aws:iam::<acct>:role/RedshiftCopyRole'
   FORMAT AS PARQUET;
   ```
2) **Redshift Data API**
   - No persistent connections; good for serverless contexts.
   - Python example: `boto3.client('redshift-data').execute_statement(...)`

**Modeling tips**
- Stage → Transform → Publish (star/snowflake)
- Use **DISTSTYLE AUTO**, **SORTKEY** on common filters; consider **MVs** for speed.

---

## Athena SQL – Examples
Put reusable queries in `athena/` and parameterize via your tooling.

Example 1: Inspect processed data
```sql
SELECT *
FROM processed_domain_table
WHERE ingest_date = DATE '2026-01-01'
LIMIT 100;
```

Example 2: Partition repair (if using Hive‑style)
```sql
MSCK REPAIR TABLE processed_domain_table;
```

Example 3: Create external table (Parquet)
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS processed_domain_table (
  id string,
  name string,
  amount decimal(18,2),
  ingest_date date
)
PARTITIONED BY (ingest_date date)
STORED AS PARQUET
LOCATION 's3://<processed-bucket>/domain/table/';
```

**Best practices**
- Prefer **CTAS** to materialize optimized Parquet.
- Use **compression (Snappy)** and **projection** for stable partitions.

---

## Step Functions – Pattern for Heavy Workflows
Use AWS Step Functions for long‑running or multi‑stage jobs (e.g., multi‑table Glue batches). Store the ASL (Amazon States Language) in `stepfunctions/`.

Minimal ASL (JSON):
```json
{
  "Comment": "ETL Orchestration",
  "StartAt": "GlueTransform",
  "States": {
    "GlueTransform": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun",
      "Parameters": {"JobName": "my-glue-job"},
      "Next": "Validate"
    },
    "Validate": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {"FunctionName": "my-validator", "Payload": {"processed_prefix.$": "$._meta.prefix"}},
      "End": true
    }
  }
}
```

**Usage tips**
- Add **Retries** with exponential backoff.
- Use **Choice** states for branching (e.g., data freshness checks).
- Emit **execution metrics** and correlate with Prefect run IDs.

---

## API Gateway → Lambda Ingestion
Use when pulling data via webhooks or offering a lightweight ingestion API.

- **API Gateway** (REST/HTTP API) receives requests and authorizes (IAM/JWT)
- **Lambda** parses payload, writes raw data to `s3://.../raw/...`, and optionally triggers Prefect or Step Functions

OpenAPI (snippet in `api-gateway/openapi.yaml`):
```yaml
paths:
  /ingest:
    post:
      x-amazon-apigateway-integration:
        type: aws_proxy
        httpMethod: POST
        uri: arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:acct:function:ingest/invocations
```

Lambda handler (pseudocode):
```python
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    # validate & write to s3 raw prefix
    # optionally call Prefect via API to start flow
    return {"statusCode": 202, "body": json.dumps({"accepted": True})}
```

**Considerations**
- Rate limits, idempotency keys, and DLQs (SQS) for resilience.
- Auth via Cognito/JWT or IAM SigV4.

---

## Testing & Quality
- Unit tests for each module (`src/aws/...`)
- Integration tests using real S3 (dev) or moto/localstack if acceptable
- Data tests: schema + row count assertions
- Linting/format: `flake8`, `black`

---

## CI/CD (optional examples)
- **CI**: run tests + lint on PRs
- **Prefect deployment**: on changes in `flows/` or `src/`
- **Glue/Lambda**: job code sync & function update steps

---

## Operations
- Observe: Prefect logs, CloudWatch (Glue/Lambda), Redshift system tables
- Alert on failures (SNS → email/Slack)
- Cost controls: Glue DPUs, Redshift WLM, Parquet + partitioning

---

## ✅ Checklist Before Production
- [ ] IAM roles with least privilege
- [ ] S3 bucket policies + encryption
- [ ] VPC endpoints + private Redshift
- [ ] Error handling & retries in flows
- [ ] Data quality checks in Lambda/Glue
- [ ] Backfills & bookmarks strategy
- [ ] CI pipelines green

---

## License & Contributions
PA's standard - PRs welcome for additional patterns (Athena CTAS, Step Functions maps, CDC, dbt models, etc.).
