import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

# -----------------------------------------------------
# Parse job parameters
# -----------------------------------------------------
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_PATH",      # e.g. s3://bucket/input/
        "TARGET_PATH",      # e.g. s3://bucket/output/
        "FORMAT",           # e.g. parquet or csv
    ]
)

source_path = args["SOURCE_PATH"]
target_path = args["TARGET_PATH"]
output_format = args["FORMAT"]

# -----------------------------------------------------
# Initialize Glue and Spark
# -----------------------------------------------------
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

print(f"Starting job with source: {source_path}, target: {target_path}")

# -----------------------------------------------------
# Extraction (TEMPLATE)
# -----------------------------------------------------
def extract_data(path: str):
    """
    Loads raw data from S3.

    Modify this depending on:
    - Different file formats
    - JDBC sources
    - Snowflake / Redshift connectors
    """
    print(f"Reading from {path}")
    df = spark.read.option("header", True).csv(path)
    return df

raw_df = extract_data(source_path)

# -----------------------------------------------------
# Transformation (TEMPLATE)
# -----------------------------------------------------
def transform_data(df):
    """
    Place all transformation logic here.
    This function is intended to be modified by each user.

    Examples:
    - Filtering
    - Casting columns
    - Dropping nulls
    - Renaming columns
    - Business logic joins
    """
    print("Applying transformations...")

    # Example transformation you can remove:
    transformed_df = (
        df
        .dropDuplicates()
        .withColumnRenamed("old_column", "new_column")
    )

    return transformed_df

processed_df = transform_data(raw_df)

# -----------------------------------------------------
# Load (TEMPLATE)
# -----------------------------------------------------
def load_data(df, path: str, fmt: str):
    """
    Writes output to S3.
    Modify this for:
    - Glue Catalog table updates
    - Partitioning
    - Snowflake unloads
    """
    print(f"Writing output to {path} in {fmt} format")

    if fmt.lower() == "parquet":
        df.write.mode("overwrite").parquet(path)
    elif fmt.lower() == "csv":
        df.write.mode("overwrite").option("header", True).csv(path)
    else:
        raise ValueError(f"Unsupported output format: {fmt}")

load_data(processed_df, target_path, output_format)

# -----------------------------------------------------
# Finish
# -----------------------------------------------------
job.commit()
print("Job completed successfully!")
