import os
import time

import boto3

from app.logger import logger


# ============================================================================
# CONFIGURATION
# ============================================================================

ATHENA_DATABASE = os.getenv(
    "ATHENA_DATABASE",
    "ai-analytics-database-malay",
)

ATHENA_OUTPUT = os.getenv(
    "ATHENA_OUTPUT",
    "s3://malay-comm-datalake-2026/athena-results/",
)

QUERY_TIMEOUT_SECONDS = 300  # 5 minute timeout

athena = boto3.client("athena")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_column_value(col: dict):
    """
    Convert Athena column value to appropriate Python type

    Args:
        col: Column dictionary from Athena response

    Returns:
        Converted value or None
    """

    if "VarCharValue" in col:
        return col["VarCharValue"]
    elif "BigIntValue" in col:
        return int(col["BigIntValue"])
    elif "DoubleValue" in col:
        return float(col["DoubleValue"])
    elif "BooleanValue" in col:
        return col["BooleanValue"].lower() == "true"
    else:
        return None


# ============================================================================
# QUERY EXECUTION
# ============================================================================

def execute_query(query: str) -> list:
    """
    Execute an Athena query and return results as list of dicts.

    Args:
        query: SQL query string to execute

    Returns:
        List of result dictionaries

    Raises:
        Exception: If query execution fails
        TimeoutError: If query exceeds timeout
    """

    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": ATHENA_DATABASE},
            ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
        )
    except Exception as e:
        logger.error(f"Failed to start Athena query: {e}")
        raise

    execution_id = response["QueryExecutionId"]
    logger.info(f"Started Athena query: {execution_id}")

    start_time = time.time()

    # ========================================================================
    # WAIT FOR QUERY COMPLETION
    # ========================================================================

    while True:

        if time.time() - start_time > QUERY_TIMEOUT_SECONDS:
            logger.error(f"Query timeout after {QUERY_TIMEOUT_SECONDS}s")
            raise TimeoutError(
                f"Athena query {execution_id} exceeded timeout of {QUERY_TIMEOUT_SECONDS}s"
            )

        try:
            status = athena.get_query_execution(QueryExecutionId=execution_id)
        except Exception as e:
            logger.error(f"Failed to get query status: {e}")
            raise

        state = status["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            logger.info(f"Query {execution_id} completed successfully")
            break

        if state in ["FAILED", "CANCELLED"]:
            failure_reason = status["QueryExecution"]["Status"].get(
                "StateChangeReason", "Unknown error"
            )
            logger.error(f"Query {execution_id} {state}: {failure_reason}")
            raise Exception(
                f"Athena query {execution_id} {state}: {failure_reason}"
            )

        logger.debug(f"Query {execution_id} state: {state}")
        time.sleep(1)

    # ========================================================================
    # FETCH RESULTS (HANDLE PAGINATION)
    # ========================================================================

    data = []
    next_token = None
    headers = None

    while True:

        try:
            result_params = {"QueryExecutionId": execution_id}
            if next_token:
                result_params["NextToken"] = next_token

            result = athena.get_query_results(**result_params)

        except Exception as e:
            logger.error(f"Failed to get query results: {e}")
            raise

        rows = result["ResultSet"]["Rows"]

        # Extract headers from first batch
        if headers is None and len(rows) > 0:
            headers = [col["VarCharValue"] for col in rows[0]["Data"]]
            # Only process data rows, skip header
            rows_to_process = rows[1:]
        else:
            # On subsequent pages, all rows are data
            rows_to_process = rows

        # Process data rows
        for row in rows_to_process:

            values = []

            for col in row["Data"]:
                values.append(convert_column_value(col))

            if headers and len(values) == len(headers):
                data.append(dict(zip(headers, values)))

        # Check for more results
        next_token = result.get("NextToken")
        if not next_token:
            break

    logger.info(f"Query {execution_id} returned {len(data)} rows")

    return data
