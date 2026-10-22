
import re


def generate_uploaded_sql(question, schema):
    """
    Generate SQLite SQL specifically for uploaded datasets.
    This function does not change the original MySQL generator.
    """

    from sql_generator import client, MODEL_NAME

    prompt = f"""
You are QueryPilot, an assistant that analyzes uploaded datasets.

TASK:
Convert the user's question into one read-only SQLite SELECT query.

UPLOADED DATASET SCHEMA:
{schema}

The uploaded data is available in one SQLite table named:
uploaded_data

USER QUESTION:
{question}

RULES:
1. Generate SQLite-compatible SQL, NOT MySQL SQL.
2. Use only the uploaded_data table.
3. Use only columns listed in the uploaded dataset schema.
4. Answer questions about counts, sums, averages, minimums,
   maximums, filtering, grouping, sorting, rankings, and comparisons.
5. Use COUNT(*) for counting records.
6. Use AVG(column) for averages, SUM(column) for totals,
   MIN(column) for minimums, and MAX(column) for maximums.
7. Use GROUP BY when comparing categories.
8. Use ORDER BY and LIMIT for ranking and top-N questions.
9. Use SQLite-compatible functions and syntax.
10. Return one SELECT query only.
11. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
    CREATE, PRAGMA, ATTACH, or other modifying statements.
12. Do not reference delivery_centers or center_daily_metrics
    unless those tables are explicitly part of the uploaded schema.
13. If the question cannot be answered from the uploaded columns,
    return exactly CANNOT_ANSWER.
14. Return only SQL or CANNOT_ANSWER.
15. Do not include Markdown fences or explanations.

Examples:
Question: How many students are in the dataset?
SQL: SELECT COUNT(*) AS total_students FROM uploaded_data

Question: What is the average weekly study hours?
SQL: SELECT AVG(Weekly_Study_Hours) AS average_study_hours FROM uploaded_data

Question: What is the highest GPA?
SQL: SELECT MAX(GPA) AS highest_gpa FROM uploaded_data

Now answer the user's question.
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            break
        except Exception as error:
            message = str(error).upper()

            if (
                ("503" in message or "UNAVAILABLE" in message)
                and attempt < 2
            ):
                import time
                time.sleep(2 * (attempt + 1))
                continue

            raise

    if response is None or not response.text:
        raise ValueError("Gemini returned an empty response.")

    sql = response.text.strip()

    # Remove Markdown code fences.
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()

    if sql.rstrip(".").upper() == "CANNOT_ANSWER":
        return "CANNOT_ANSWER"

    return sql
