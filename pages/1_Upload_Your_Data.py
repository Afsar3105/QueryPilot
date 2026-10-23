import hashlib
import io
import re
import sqlite3
import time
import uuid
from pathlib import Path

import pandas as pd
import sqlglot
import streamlit as st
from sqlglot import exp

from sql_generator import generate_summary
from uploaded_data.sql_generator_upload import generate_uploaded_sql


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QueryPilot | Upload Your Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_DIR / "uploaded_data"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 25
MAX_ROWS = 500_000
MAX_COLUMNS = 200
DB_TABLE_NAME = "uploaded_data"


# ============================================================
# STYLING
# ============================================================


st.markdown(
    """
    <style>
    /* ==========================================
       QUERYPILOT — UPLOAD YOUR DATA
       Unified four-colour theme
       ========================================== */

    /* Main page */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #FFFAFA !important;
        color: #000080 !important;
    }

    [data-testid="stMain"] .block-container {
        max-width: 1500px;
        padding-top: 2rem !important;
        padding-bottom: 2.5rem !important;
        color: #000080 !important;
    }

    /* Headings and readable body text */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5,
    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] li,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"] {
        color: #000080 !important;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        font-weight: 700 !important;
    }

    /* Top toolbar */
    header[data-testid="stHeader"] {
        background-color: #FFFAFA !important;
    }

    [data-testid="stDecoration"] {
        background-color: #6D8196 !important;
    }

    /* ==========================================
       SIDEBAR — MATCH DATABASE EXPLORER
       ========================================== */

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #000080 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #FFFAFA !important;
    }

    /* QueryPilot branding */
    .querypilot-brand {
        padding: 10px 2px 18px 2px;
    }

    .querypilot-brand-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #FFFAFA !important;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.3;
    }

    .brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background-color: #6D8196 !important;
        color: #FFFAFA !important;
        font-size: 24px;
        font-weight: 800;
    }

    .querypilot-brand-subtitle {
        margin-top: 8px;
        color: #ADD8E6 !important;
        font-size: 13px;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Sidebar navigation buttons */
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
        display: flex;
        align-items: center;
        min-height: 46px;
        padding: 10px 12px !important;
        margin: 7px 0;
        background-color: #6D8196 !important;
        border: 1px solid #ADD8E6 !important;
        border-radius: 10px !important;
        color: #FFFAFA !important;
        font-weight: 700 !important;
        text-decoration: none !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p,
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span {
        color: #FFFAFA !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
        background-color: #ADD8E6 !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover,
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover p,
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover span {
        color: #000080 !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
        background-color: #ADD8E6 !important;
        border: 2px solid #FFFAFA !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] p,
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] span {
        color: #000080 !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        min-height: 44px;
        background-color: #6D8196 !important;
        color: #FFFAFA !important;
        border: 1px solid #ADD8E6 !important;
        border-radius: 10px !important;
        font-weight: 650 !important;
        box-shadow: none !important;
        transition: background-color 0.2s ease;
    }

    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stButton > button span {
        color: #FFFAFA !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #ADD8E6 !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover,
    section[data-testid="stSidebar"] div.stButton > button:hover p,
    section[data-testid="stSidebar"] div.stButton > button:hover span {
        color: #000080 !important;
    }

    /* ==========================================
       HERO / BRAND CARD
       ========================================== */

    .hero-card {
        padding: 26px 30px;
        margin: 8px 0 24px 0;
        background-color: #000080 !important;
        color: #FFFAFA !important;
        border: 2px solid #6D8196;
        border-radius: 16px;
        box-shadow: none !important;
    }

    .hero-card h1,
    .hero-card h2,
    .hero-card p {
        color: #FFFAFA !important;
    }

    /* ==========================================
       BUTTONS
       ========================================== */

    div.stButton > button {
        min-height: 42px;
        background-color: #ADD8E6 !important;
        color: #000080 !important;
        border: 1px solid #6D8196 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }

    div.stButton > button p,
    div.stButton > button span {
        color: #000080 !important;
    }

    div.stButton > button:hover {
        background-color: #6D8196 !important;
    }

    div.stButton > button:hover,
    div.stButton > button:hover p,
    div.stButton > button:hover span {
        color: #FFFAFA !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #000080 !important;
        color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
    }

    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        color: #FFFAFA !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #6D8196 !important;
    }

    /* ==========================================
       FILE UPLOADER
       ========================================== */

    [data-testid="stFileUploader"] {
        background-color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #ADD8E6 !important;
        border: 1px dashed #6D8196 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #6D8196 !important;
        color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploader"] button span,
    [data-testid="stFileUploader"] button p {
        color: #FFFAFA !important;
    }

    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {
        color: #000080 !important;
    }

    /* ==========================================
       INPUTS AND SELECTORS
       ========================================== */

    [data-testid="stMain"] input,
    [data-testid="stMain"] textarea,
    [data-testid="stMain"] [data-baseweb="select"] > div {
        background-color: #FFFAFA !important;
        color: #000080 !important;
        border-color: #6D8196 !important;
    }

    /* ==========================================
       TABLES, METRICS AND EXPANDERS
       ========================================== */

    [data-testid="stMetric"] {
        background-color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: none !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #000080 !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background-color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] {
        background-color: #FFFAFA !important;
        border: 1px solid #6D8196 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p {
        color: #000080 !important;
    }

    /* Alerts and status messages */
    [data-testid="stAlert"] {
        background-color: #ADD8E6 !important;
        border: 1px solid #6D8196 !important;
        border-radius: 10px !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #000080 !important;
    }

    /* Code blocks */
    [data-testid="stMain"] code {
        background-color: #ADD8E6 !important;
        color: #000080 !important;
    }

    /* Keyboard focus */
    .stApp button:focus-visible,
    section[data-testid="stSidebar"] a:focus-visible {
        outline: 2px solid #6D8196 !important;
        outline-offset: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

SESSION_DEFAULTS = {
    "qp_upload_db_path": None,
    "qp_upload_file_path": None,
    "qp_upload_file_name": None,
    "qp_upload_dataframe": None,
    "qp_upload_chat": [],
    "qp_upload_signature": None,
    "qp_pending_question": None,
    "qp_upload_active_view": {},
    "qp_upload_empty_question": False,
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FILE / DATA HELPERS
# ============================================================

def cleanup_old_files(max_age_hours=24):
    """Best-effort cleanup for old temporary QueryPilot upload files."""
    cutoff = time.time() - max_age_hours * 3600
    try:
        for path in UPLOAD_DIR.glob("qp_upload_*"):
            try:
                if path.is_file() and path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
    except OSError:
        pass


def delete_current_upload():
    """Delete the active temporary SQLite database and uploaded file."""
    for key in ("qp_upload_db_path", "qp_upload_file_path"):
        path_value = st.session_state.get(key)
        if path_value:
            try:
                Path(path_value).unlink(missing_ok=True)
            except (OSError, TypeError, ValueError):
                pass

    for key, value in SESSION_DEFAULTS.items():
        st.session_state[key] = value


def normalize_columns(dataframe):
    """Make column names safe and predictable for generated SQL."""
    dataframe = dataframe.copy()
    cleaned = []
    used = set()

    for index, original in enumerate(dataframe.columns, start=1):
        name = str(original).strip().lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")

        if not name:
            name = f"column_{index}"
        if name[0].isdigit():
            name = f"col_{name}"

        base = name
        suffix = 2
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1

        used.add(name)
        cleaned.append(name)

    dataframe.columns = cleaned
    return dataframe


def read_uploaded_file(uploaded_file, sheet_name=None):
    """Read CSV or Excel data into a DataFrame."""
    raw = uploaded_file.getvalue()

    if len(raw) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Please upload a file smaller than {MAX_FILE_SIZE_MB} MB.")

    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix == ".csv":
        try:
            dataframe = pd.read_csv(io.BytesIO(raw))
        except UnicodeDecodeError:
            dataframe = pd.read_csv(io.BytesIO(raw), encoding="latin-1")
    elif suffix in (".xlsx", ".xls"):
        dataframe = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name or 0)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")

    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError("Could not read the selected worksheet.")

    if dataframe.empty:
        raise ValueError("The selected file or worksheet contains no data.")

    if len(dataframe) > MAX_ROWS:
        raise ValueError(f"The file contains more than {MAX_ROWS:,} rows.")
    if len(dataframe.columns) > MAX_COLUMNS:
        raise ValueError(f"The file contains more than {MAX_COLUMNS} columns.")

    dataframe = normalize_columns(dataframe)
    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()]
    return dataframe


def create_uploaded_database(dataframe):
    """Create an isolated temporary SQLite database for the uploaded dataset."""
    token = uuid.uuid4().hex
    db_path = UPLOAD_DIR / f"qp_upload_{token}.sqlite"
    file_path = UPLOAD_DIR / f"qp_upload_{token}.source"

    connection = sqlite3.connect(str(db_path))
    try:
        dataframe.to_sql(DB_TABLE_NAME, connection, if_exists="replace", index=False)
    finally:
        connection.close()

    st.session_state["qp_upload_db_path"] = str(db_path)
    st.session_state["qp_upload_file_path"] = str(file_path)
    st.session_state["qp_upload_dataframe"] = dataframe
    return str(db_path)


def build_schema(dataframe):
    """Build a schema description for the text-to-SQL model."""
    column_lines = []
    for column in dataframe.columns:
        dtype = str(dataframe[column].dtype)
        column_lines.append(f"  - {column} ({dtype})")

    return (
        "SQLite database. One table is available:\n"
        f"Table: {DB_TABLE_NAME}\n"
        "Columns:\n"
        + "\n".join(column_lines)
        + f"\nOnly query the table {DB_TABLE_NAME}."
    )


def validate_and_convert_sql(sql):
    """Allow only one safe SELECT query against uploaded_data."""
    if not sql or not isinstance(sql, str):
        raise ValueError("The SQL generator did not return a query.")

    sql = sql.strip().rstrip(";")
    if not sql:
        raise ValueError("The generated SQL query is empty.")

    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as error:
        raise ValueError(f"The generated SQL could not be parsed: {error}") from error

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    tree = statements[0]
    if not isinstance(tree, exp.Query):
        raise ValueError("Only read-only SELECT queries are allowed.")

    forbidden_types = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.TruncateTable,
        exp.Command,
    )
    if any(tree.find(node_type) for node_type in forbidden_types):
        raise ValueError("Only read-only SELECT queries are allowed.")

    table_names = {
        table.name.lower()
        for table in tree.find_all(exp.Table)
    }
    if not table_names:
        raise ValueError(f"Your query must use the {DB_TABLE_NAME} table.")

    if any(name != DB_TABLE_NAME for name in table_names):
        raise ValueError(f"Queries may only use the {DB_TABLE_NAME} table.")

    # Add a safety limit unless the query already specifies a limit.
    if not tree.args.get("limit"):
        tree = tree.limit(1000)

    return tree.sql(dialect="sqlite")


def run_uploaded_query(sql):
    """Run a validated query on the temporary uploaded-data database."""
    db_path = st.session_state.get("qp_upload_db_path")
    if not db_path or not Path(db_path).exists():
        raise RuntimeError("Your uploaded dataset is no longer available. Please upload it again.")

    safe_sql = validate_and_convert_sql(sql)
    connection = sqlite3.connect(f"file:{Path(db_path).resolve().as_posix()}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(safe_sql, connection)
    finally:
        connection.close()


def format_value(value):
    try:
        if pd.isna(value):
            return "—"
        if isinstance(value, (int, float)) and float(value).is_integer():
            return f"{int(value):,}"
        if isinstance(value, (int, float)):
            return f"{value:,.2f}"
    except (TypeError, ValueError):
        pass
    return str(value)


def set_active_view(record_id, view):
    st.session_state["qp_upload_active_view"][record_id] = view


def show_visual_analysis(record, record_id):
    """Show only the visualization selected for this answer."""
    results = record.get("results")
    if results is None or results.empty:
        return

    st.markdown("#### Visual Analysis")
    button_cols = st.columns(4)

    options = [
        ("📊 Show bar chart", "bar"),
        ("📈 Show line chart", "line"),
        ("🔢 Show KPI chart", "kpi"),
        ("💡 Show explanation", "explanation"),
    ]

    for col, (label, view) in zip(button_cols, options):
        with col:
            st.button(
                label,
                key=f"{record_id}_{view}_button",
                use_container_width=True,
                on_click=set_active_view,
                args=(record_id, view),
            )

    selected_view = st.session_state["qp_upload_active_view"].get(record_id)
    if not selected_view:
        return

    numeric_columns = results.select_dtypes(include="number").columns.tolist()
    non_numeric_columns = [
        column for column in results.columns
        if column not in numeric_columns
    ]

    if selected_view in ("bar", "line"):
        if not numeric_columns:
            st.info("This result does not contain numeric columns to chart.")
            return

        metric_col = numeric_columns[0]
        if non_numeric_columns:
            category_col = non_numeric_columns[0]
            chart_data = results[[category_col, metric_col]].copy()
            chart_data[metric_col] = pd.to_numeric(chart_data[metric_col], errors="coerce")
            chart_data = chart_data.dropna(subset=[metric_col])

            if chart_data.empty:
                st.info("There is no numeric data available for this chart.")
                return

            chart_data[category_col] = chart_data[category_col].astype(str)
            chart_data = chart_data.set_index(category_col)
            if selected_view == "bar":
                st.bar_chart(chart_data[metric_col])
            else:
                st.line_chart(chart_data[metric_col])
        elif len(numeric_columns) >= 2:
            chart_data = results[numeric_columns].apply(pd.to_numeric, errors="coerce")
            if selected_view == "bar":
                st.bar_chart(chart_data)
            else:
                st.line_chart(chart_data)
        else:
            st.info("Add a category column to your question for a more useful chart.")

    elif selected_view == "kpi":
        if not numeric_columns:
            st.info("This result does not contain numeric values for KPI cards.")
            return

        cols = st.columns(min(4, len(numeric_columns)))
        for index, column in enumerate(numeric_columns[:4]):
            numeric_values = pd.to_numeric(results[column], errors="coerce").dropna()
            if numeric_values.empty:
                value = "—"
            elif len(results) == 1:
                value = format_value(numeric_values.iloc[0])
            else:
                value = format_value(numeric_values.sum())
            with cols[index]:
                st.metric(column.replace("_", " ").title(), value)

    elif selected_view == "explanation":
        st.write(record.get("summary") or "The query completed. Review the results above.")


def process_question(question):
    """Generate SQL, execute it, and store the answer in chat history."""
    dataframe = st.session_state.get("qp_upload_dataframe")
    if dataframe is None:
        st.warning("Upload a CSV or Excel file before asking a question.")
        return

    record_id = uuid.uuid4().hex[:10]
    record = {
        "id": record_id,
        "question": question,
        "sql": None,
        "results": None,
        "summary": None,
        "status": "success",
        "error": None,
    }

    try:
        with st.spinner("QueryPilot is analyzing your question..."):
            schema = build_schema(dataframe)
            sql = generate_uploaded_sql(question, schema)

            if sql == "CANNOT_ANSWER":
                record["status"] = "cannot_answer"
            else:
                record["sql"] = sql
                results = run_uploaded_query(sql)
                record["results"] = results

                try:
                    record["summary"] = generate_summary(question, sql, results)
                except Exception:
                    record["summary"] = (
                        "The query completed successfully. Review the results below; "
                        "an AI explanation could not be generated."
                    )

    except Exception as error:
        record["status"] = "error"
        record["error"] = str(error)

    st.session_state["qp_upload_chat"].append(record)


def submit_question():
    question = st.session_state.get("qp_shared_question", "").strip()
    st.session_state["qp_pending_question"] = question



# ============================================================
# SIDEBAR
# ============================================================

cleanup_old_files()

with st.sidebar:

    # QueryPilot branding
    st.markdown(
        """
        <div class="querypilot-brand">
            <div class="querypilot-brand-title">
                <span class="brand-icon">▤</span>
                <span>QueryPilot</span>
            </div>
            <div class="querypilot-brand-subtitle">
                AI-powered Operations Analytics
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Delete uploaded dataset
    if st.button(
        "🗑️ Delete Uploaded Data",
        key="delete_uploaded_data_sidebar",
        use_container_width=True,
        type="secondary",
    ):
        delete_current_upload()
        st.rerun()

    # Start a fresh upload/chat
    if st.button(
        "＋ New Upload / New Chat",
        key="new_upload_chat_sidebar",
        use_container_width=True,
        type="primary",
    ):
        delete_current_upload()
        st.rerun()

    st.divider()

    # Instructions
    st.markdown("### How to use")

    st.caption("1. Upload a CSV or Excel file.")
    st.caption("2. Select a worksheet if needed.")
    st.caption("3. Ask questions in plain English.")
    st.caption("4. View SQL, results, charts, and explanations.")

    st.divider()

    st.caption(
        "Your uploaded data uses a temporary SQLite database "
        "and does not change the main QueryPilot MySQL database."
    )



# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <h1>QueryPilot — Upload Your Data</h1>
        <p>Upload a spreadsheet, ask questions in plain English, and explore your data with SQL, results, KPIs, and charts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD DATA
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your data",
    type=["csv", "xlsx", "xls"],
    help=f"Maximum file size: {MAX_FILE_SIZE_MB} MB.",
)

selected_sheet = None
if uploaded_file is not None and Path(uploaded_file.name).suffix.lower() in (".xlsx", ".xls"):
    try:
        excel_file = pd.ExcelFile(io.BytesIO(uploaded_file.getvalue()))
        if excel_file.sheet_names:
            selected_sheet = st.selectbox(
                "Choose worksheet",
                options=excel_file.sheet_names,
                key="qp_excel_sheet",
            )
    except Exception as error:
        st.error(f"Could not read the Excel workbook: {error}")

if uploaded_file is not None:
    file_signature = hashlib.sha256(
        uploaded_file.getvalue() + str(selected_sheet).encode("utf-8")
    ).hexdigest()

    if file_signature != st.session_state.get("qp_upload_signature"):
        try:
            new_dataframe = read_uploaded_file(uploaded_file, selected_sheet)
            delete_current_upload()
            create_uploaded_database(new_dataframe)

            st.session_state["qp_upload_file_name"] = uploaded_file.name
            st.session_state["qp_upload_signature"] = file_signature
            st.session_state["qp_upload_chat"] = []
            st.session_state["qp_upload_active_view"] = {}
            st.success(f"Successfully loaded **{uploaded_file.name}**.")
        except Exception as error:
            st.error(f"Unable to load this file: {error}")

dataframe = st.session_state.get("qp_upload_dataframe")


# ============================================================
# DATASET OVERVIEW
# ============================================================

if dataframe is not None:
    st.markdown("### Dataset overview")
    st.caption(f"File: {st.session_state.get('qp_upload_file_name', 'Uploaded dataset')}")

    total_rows, total_columns = dataframe.shape
    missing_values = int(dataframe.isna().sum().sum())

    metrics = st.columns(3)
    metrics[0].metric("Rows", f"{total_rows:,}")
    metrics[1].metric("Columns", f"{total_columns:,}")
    metrics[2].metric("Missing values", f"{missing_values:,}")

    with st.expander("Preview uploaded data", expanded=True):
        st.dataframe(dataframe.head(10), use_container_width=True, hide_index=True)

    with st.expander("Detected columns and data types"):
        schema_table = pd.DataFrame({
            "Column": dataframe.columns,
            "Data type": [str(dataframe[column].dtype) for column in dataframe.columns],
            "Missing values": [int(dataframe[column].isna().sum()) for column in dataframe.columns],
        })
        st.dataframe(schema_table, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Ask questions about your data")
    st.caption("Examples: Which region has the highest net sales? What is the total number of units sold? Show monthly sales.")


# ============================================================
# PROCESS PENDING QUESTION BEFORE RENDERING CHAT
# ============================================================

pending_question = st.session_state.get("qp_pending_question")
st.session_state["qp_pending_question"] = None

if pending_question is not None:
    if not pending_question.strip():
        st.session_state["qp_upload_empty_question"] = True
    else:
        st.session_state["qp_upload_empty_question"] = False
        process_question(pending_question.strip())

if st.session_state.get("qp_upload_empty_question"):
    st.warning("Please enter a question first.")


# ============================================================
# RENDER CHAT HISTORY
# ============================================================

for index, record in enumerate(st.session_state["qp_upload_chat"]):
    with st.chat_message("user"):
        st.markdown(record["question"])

    with st.chat_message("assistant"):
        if record["status"] == "cannot_answer":
            st.info(
                "I couldn't answer this question using the available columns. "
                "Try asking a question that can be answered from the uploaded dataset."
            )
            continue

        if record["status"] == "error":
            st.error("QueryPilot couldn't complete this request.")
            with st.expander("Technical details"):
                st.code(record.get("error") or "Unknown error")
            if record.get("sql"):
                with st.expander("Generated SQL"):
                    st.code(record["sql"], language="sql")
            continue

        if record.get("sql"):
            with st.expander("View generated SQL", expanded=False):
                st.code(record["sql"], language="sql")

        results = record.get("results")
        if results is None:
            st.info("No results are available for this question.")
            continue

        st.markdown("#### Query results")
        if results.empty:
            st.info("No matching records were found.")
        else:
            st.dataframe(results, use_container_width=True, hide_index=True)
            st.caption(f"Returned {len(results):,} row(s).")

        st.markdown("#### What this means")
        st.write(record.get("summary") or "The query completed. Review the results above.")

        if results is not None and not results.empty:
            show_visual_analysis(record, record["id"])

        st.divider()


# ============================================================
# ONE SHARED QUESTION BOX — OUTSIDE THE CHAT LOOP
# ============================================================

if dataframe is not None:
    with st.form("qp_shared_question_form", clear_on_submit=True):
        st.text_input(
            "Ask another question",
            placeholder="e.g., Which region has the highest net sales?",
            key="qp_shared_question",
        )
        submitted = st.form_submit_button(
            "Ask QueryPilot →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        question = st.session_state.get("qp_shared_question", "").strip()
        st.session_state["qp_pending_question"] = question
        st.rerun()
else:
    st.info("Upload a CSV or Excel file to begin analyzing your data.")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "QueryPilot | AI-powered Data Analytics | "
    "Uploaded data is processed in a temporary SQLite database separate from your main MySQL database."
)

