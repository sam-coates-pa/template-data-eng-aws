import logging
import psycopg2
from psycopg2 import sql
import time

# -----------------------------------------------------
# Logging
# -----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Redshift Connection
# -----------------------------------------------------
def get_redshift_connection(
    host: str,
    port: int,
    db: str,
    user: str,
    password: str
):
    """
    Creates a Redshift connection using psycopg2.
    """
    try:
        logger.info("Connecting to Redshift...")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db,
            user=user,
            password=password
        )
        conn.autocommit = True
        return conn

    except Exception as e:
        logger.error(f"Failed to connect to Redshift: {e}")
        raise


# -----------------------------------------------------
# COPY Command Executor
# -----------------------------------------------------
def copy_to_redshift(
    conn,
    table: str,
    s3_path: str,
    iam_role_arn: str,
    region: str = "eu-west-2",
    format: str = "JSON",
    jsonpath: str = "auto"
):
    """
    Executes a Redshift COPY command.

    :param conn: psycopg2 connection
    :param table: Target Redshift table
    :param s3_path: S3 URI to load from
    :param iam_role_arn: IAM role with Redshift COPY permissions
    :param region: AWS region for S3
    :param format: 'JSON' or 'CSV'
    :param jsonpath: 'auto' or path to JSONPaths file
    """
    cursor = conn.cursor()

    logger.info(f"Starting COPY into {table} from {s3_path}")

    if format.upper() == "JSON":
        copy_sql = sql.SQL("""
            COPY {table}
            FROM %s
            IAM_ROLE %s
            REGION %s
            FORMAT AS JSON %s;
        """).format(table=sql.Identifier(table))

        params = (s3_path, iam_role_arn, region, jsonpath)

    elif format.upper() == "CSV":
        copy_sql = sql.SQL("""
            COPY {table}
            FROM %s
            IAM_ROLE %s
            REGION %s
            CSV
            IGNOREHEADER 1;
        """).format(table=sql.Identifier(table))

        params = (s3_path, iam_role_arn, region)

    else:
        raise ValueError("Unsupported file format. Use JSON or CSV.")

    try:
        cursor.execute(copy_sql, params)
        logger.info(f"COPY command executed successfully for table {table}")

    except Exception as e:
        logger.error(f"COPY command failed: {e}")
        raise

    finally:
        cursor.close()


# -----------------------------------------------------
# High-Level Loader Function
# -----------------------------------------------------
def load_to_redshift(
    host: str,
    port: int,
    db: str,
    user: str,
    password: str,
    table: str,
    s3_path: str,
    iam_role_arn: str,
    region: str = "eu-west-2",
    format: str = "JSON",
    jsonpath: str = "auto"
) -> dict:
    """
    Full Redshift Load (connect → copy → close).
    Returns metadata about the load.
    """

    conn = get_redshift_connection(host, port, db, user, password)

    try:
        start_time = time.time()

        copy_to_redshift(
            conn=conn,
            table=table,
            s3_path=s3_path,
            iam_role_arn=iam_role_arn,
            region=region,
            format=format,
            jsonpath=jsonpath
        )

        duration = time.time() - start_time

        result = {
            "table": table,
            "s3_path": s3_path,
            "status": "SUCCESS",
            "duration_seconds": round(duration, 2)
        }

        logger.info(f"Load completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise

    finally:
        conn.close()
        logger.info("Redshift connection closed.")


# -----------------------------------------------------
# Local Test (Optional)
# -----------------------------------------------------
if __name__ == "__main__":
    output = load_to_redshift(
        host="redshift-cluster.xxxx.eu-west-2.redshift.amazonaws.com",
        port=5439,
        db="dev",
        user="awsuser",
        password="mypassword",
        table="raw_events",
        s3_path="s3://my-bucket/data/events/",
        iam_role_arn="arn:aws:iam::123456789012:role/RedshiftCopyRole"
    )
    print(output)
