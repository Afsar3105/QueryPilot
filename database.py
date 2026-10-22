
import os

import mysql.connector
import pandas as pd
import sqlglot
import streamlit as st
from sqlglot import exp
from dotenv import load_dotenv

load_dotenv()

ALLOWED_TABLES = {
    "delivery_centers",
    "center_daily_metrics",
}

MAX_ROWS = 100


def get_setting(name, default=""):
    """Read settings from Streamlit Secrets or local environment."""
    try:
        value = st.secrets.get(name, None)
    except Exception:
        value = None

    if value is None or value == "":
        value = os.getenv(name, default)

    if value is None:
        return default

    return str(value).strip()


def get_connection(read_only=True):
    """Connect to the QueryPilot MySQL database."""
    config = {
        "host": get_setting("DB_HOST", "127.0.0.1"),
        "port": int(get_setting("DB_PORT", "3306")),
        "database": get_setting("DB_NAME", "querypilot"),
        "user": get_setting("DB_USER"),
        "password": get_setting("DB_PASSWORD"),
        "connection_timeout": 10,
    }

    # Aiven requires an encrypted connection.
    if config["host"] != "127.0.0.1" and config["host"] != "localhost":
        config["ssl_disabled"] = False

    if not config["user"] or not config["password"]:
        raise ValueError(
            "Set DB_USER and DB_PASSWORD in your local .env "
            "or Streamlit Cloud Secrets."
        )

    connection = mysql.connector.connect(**config)

    if read_only:
        cursor = connection.cursor()
        try:
            cursor.execute("SET SESSION TRANSACTION READ ONLY")
        finally:
            cursor.close()

    return connection


def get_schema():
    """Return the approved tables and their columns."""
    connection = get_connection()

    try:
        cursor = connection.cursor()
        schema_parts = []

        for table in sorted(ALLOWED_TABLES):
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [row[0] for row in cursor.fetchall()]

            schema_parts.append(
                f"Table: {table}\n"
                f"Columns: {', '.join(columns)}"
            )

        cursor.close()
        return "\n\n".join(schema_parts)

    finally:
        connection.close()


def validate_sql(sql):
    """Allow a single SELECT query using approved tables only."""
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("The generated SQL is empty.")

    if ";" in sql.rstrip().rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    if "--" in sql or "/*" in sql or "#" in sql:
        raise ValueError("SQL comments are not allowed.")

    cleaned_sql = sql.strip().rstrip(";").strip()

    try:
        statements = sqlglot.parse(cleaned_sql, read="mysql")
    except Exception as error:
        raise ValueError("The generated SQL is invalid.") from error

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    query = statements[0]

    if not isinstance(query, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    if query.args.get("into") is not None:
        raise ValueError("SELECT INTO is not allowed.")

    if query.args.get("locks"):
        raise ValueError("Locking clauses are not allowed.")

    for table in query.find_all(exp.Table):
        if table.name.lower() not in ALLOWED_TABLES:
            raise ValueError(
                f"Table '{table.name}' is not approved."
            )

        if table.db or table.catalog:
            raise ValueError(
                "Cross-database references are not allowed."
            )

    blocked_functions = {
        "SLEEP",
        "BENCHMARK",
        "LOAD_FILE",
    }

    for node in query.walk():
        if isinstance(node, exp.Func):
            function_name = node.sql_name().upper()

            if function_name in blocked_functions:
                raise ValueError(
                    f"Function '{function_name}' is not allowed."
                )

    return cleaned_sql


def run_generated_query(sql):
    """Validate and execute a read-only analytics query."""
    safe_sql = validate_sql(sql)

    connection = get_connection(read_only=True)

    try:
        connection.start_transaction(readonly=True)

        limited_sql = (
            f"SELECT * FROM ({safe_sql}) AS querypilot_result "
            f"LIMIT {MAX_ROWS + 1}"
        )

        results = pd.read_sql_query(limited_sql, connection)

        if len(results) > MAX_ROWS:
            results = results.head(MAX_ROWS)

        return results

    finally:
        if connection.in_transaction:
            connection.rollback()

        connection.close()
