import time
import streamlit as st
import pandas as pd

from sql_generator import generate_sql, generate_summary
from database import get_schema, run_generated_query


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="QueryPilot | AI-Powered Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PROFESSIONAL STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    
       
.stApp {
    background-color: #f5f7fb;
    color: #1f2937;
}

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #0f172a !important;
}

.stApp p,
.stApp label {
    color: #334155;
}

.stApp .hero-card,
.stApp .hero-card h1 {
    color: #ffffff !important;
}

.stApp .hero-card p {
    color: #e0eaff !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    color: #0f172a !important;
}



    [data-testid="stSidebar"] {
        background-color: #101b33;
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9;
    }

    .hero-card {
        padding: 26px;
        border-radius: 18px;
        background: linear-gradient(120deg, #0f766e, #134e4a);
        color: white;
        margin-bottom: 24px;
    }

    .hero-card h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero-card p {
        color: #e0eaff;
        margin-bottom: 0;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #0f766e, #14b8a6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    div.stButton > button {
        border-radius: 10px;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border: 1px solid #e5eaf3;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
    }

    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 10px;
    }

    
/* ===== QUERYPILOT SIDEBAR CHAT HISTORY ===== */

/* Keep sidebar dark and premium */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1224 0%, #111d35 100%);
}

/* Default sidebar buttons */
section[data-testid="stSidebar"] div.stButton > button {
    background: #173b3b !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(148, 163, 184, 0.16) !important;
    border-radius: 14px !important;
    min-height: 46px;
    font-weight: 600 !important;
    transition:
        background 0.25s ease,
        color 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease !important;
}

/* Keep all nested button text visible */
section[data-testid="stSidebar"] div.stButton > button p,
section[data-testid="stSidebar"] div.stButton > button span {
    color: #f1f5f9 !important;
}

/* Stunning hover effect */
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: linear-gradient(
        110deg,
        #0f766e 0%,
        #0d9488 55%,
        #14b8a6 100%
    ) !important;
    color: #ffffff !important;
    border-color: rgba(94, 234, 212, 0.9) !important;
    box-shadow:
        0 0 0 1px rgba(45, 212, 191, 0.18),
        0 8px 24px rgba(13, 148, 136, 0.30) !important;
    transform: translateY(-2px) scale(1.01);
}

/* Ensure hover text stays white */
section[data-testid="stSidebar"] div.stButton > button:hover p,
section[data-testid="stSidebar"] div.stButton > button:hover span {
    color: #ffffff !important;
}

/* Keyboard focus */
section[data-testid="stSidebar"] div.stButton > button:focus-visible {
    outline: 2px solid #5eead4 !important;
    outline-offset: 3px;
}

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
}

/* Sidebar captions and supporting text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #cbd5e1;
}

/* Native multipage navigation: clear, bold labels */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 12px !important;
    font-weight: 700 !important;
    margin: 4px 0 !important;
    padding: 10px 12px !important;
    transition: background 0.2s ease, transform 0.2s ease !important;
}

/* Make Upload Your Data the most visible navigation item */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[href*="Upload_Your_Data"] {
    background: linear-gradient(110deg, #0f766e, #14b8a6) !important;
    border: 1px solid rgba(94, 234, 212, 0.65) !important;
    box-shadow: 0 6px 18px rgba(13, 148, 136, 0.22) !important;
    margin-top: 8px !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[href*="Upload_Your_Data"]:hover {
    background: linear-gradient(110deg, #115e59, #0f766e) !important;
    transform: translateY(-1px);
}

/* Keep the active navigation item easy to identify */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    border: 1px solid rgba(94, 234, 212, 0.7) !important;
    background-color: rgba(15, 118, 110, 0.42) !important;
}



/* ==========================================
   QUERYPILOT PROFESSIONAL SIDEBAR
   ========================================== */

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b1224 0%,
        #102238 100%
    ) !important;
}

/* QueryPilot brand area */
.querypilot-brand {
    padding: 10px 2px 18px 2px;
}

.querypilot-brand-title {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #ffffff;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.3;
}

.brand-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #134e4a;
    color: #5eead4;
    font-size: 25px;
    font-weight: 800;
}

.querypilot-brand-subtitle {
    margin-top: 8px;
    color: #a8b8c9;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.5;
}

/* Hide automatic navigation so it doesn't appear
   above the custom QueryPilot branding */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none;
}

/* Main page navigation links */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    display: flex;
    align-items: center;
    min-height: 48px;
    padding: 11px 14px !important;
    margin: 7px 0;
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 12px;
    color: #f8fafc !important;
    font-weight: 750 !important;
    transition: all 0.2s ease;
}

/* Ensure navigation text stays bold and visible */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p,
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span {
    color: #f8fafc !important;
    font-weight: 750 !important;
}

/* Highlight Upload Your Data */
section[data-testid="stSidebar"] a[href*="Upload_Your_Data"] {
    background: linear-gradient(
        110deg,
        #0f766e,
        #14b8a6
    ) !important;
    border: 1px solid #5eead4 !important;
    box-shadow: 0 5px 16px rgba(13, 148, 136, 0.20);
}

/* Navigation hover */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: #164e4a !important;
    border-color: #5eead4 !important;
    transform: translateY(-1px);
}

/* Sidebar section headings */
section[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 750 !important;
}

/* New Chat and chat history buttons */
section[data-testid="stSidebar"] div.stButton > button {
    border-radius: 11px !important;
    font-weight: 650 !important;
    min-height: 43px;
}

/* Keyboard accessibility */
section[data-testid="stSidebar"] a:focus-visible,
section[data-testid="stSidebar"] button:focus-visible {
    outline: 2px solid #5eead4 !important;
    outline-offset: 3px;
}


    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE: CHAT STORAGE
# --------------------------------------------------

if "chats" not in st.session_state:
    st.session_state["chats"] = {
        "chat_1": {
            "title": "New chat",
            "messages": [],
        }
    }
    st.session_state["active_chat_id"] = "chat_1"
    st.session_state["chat_counter"] = 1

if "active_chat_id" not in st.session_state:
    st.session_state["active_chat_id"] = "chat_1"

if "pending_question" not in st.session_state:
    st.session_state["pending_question"] = None

if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""


# --------------------------------------------------
# CHAT ACTIONS
# --------------------------------------------------

def create_new_chat():
    """Create a new conversation without deleting old chats."""
    current_id = st.session_state["active_chat_id"]
    current_chat = st.session_state["chats"].get(current_id, {})

    # Avoid creating multiple empty chats.
    if not current_chat.get("messages"):
        st.session_state["question_input"] = ""
        return

    st.session_state["chat_counter"] += 1
    new_id = f"chat_{st.session_state['chat_counter']}"

    st.session_state["chats"][new_id] = {
        "title": "New chat",
        "messages": [],
    }

    st.session_state["active_chat_id"] = new_id
    st.session_state["question_input"] = ""


def switch_chat(chat_id):
    """Open an existing conversation."""
    st.session_state["active_chat_id"] = chat_id
    st.session_state["question_input"] = ""


def submit_question():
    """Capture the question and clear the input before rerunning."""
    question = st.session_state.get("question_input", "").strip()
    st.session_state["pending_question"] = question
    st.session_state["question_input"] = ""


# --------------------------------------------------
# DATA DISPLAY HELPERS
# --------------------------------------------------


def set_suggested_question(question):
    """Fill the existing question input with a suggested question."""
    st.session_state["question_input"] = question



@st.cache_data(ttl=60, show_spinner=False)
def load_database_overview():
    """Load a small overview from the hosted QueryPilot database."""
    overview_sql = """
        SELECT
            (SELECT COUNT(*) FROM delivery_centers)
                AS delivery_center_count,
            (SELECT COUNT(*) FROM center_daily_metrics)
                AS metric_record_count,
            (SELECT COUNT(DISTINCT city) FROM delivery_centers)
                AS city_count
    """

    preview_sql = """
        SELECT store_code, city, state
        FROM delivery_centers
        ORDER BY city
        LIMIT 5
    """

    overview = run_generated_query(overview_sql)
    preview = run_generated_query(preview_sql)

    return overview, preview



def format_number(value):
    if pd.isna(value):
        return "—"

    try:
        number = float(value)

        if number.is_integer():
            return f"{int(number):,}"

        return f"{number:,.2f}"

    except (ValueError, TypeError):
        return str(value)


def find_column(dataframe, candidates):
    """Find a column without depending on capitalization."""
    column_lookup = {
        str(column).lower(): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        if candidate.lower() in column_lookup:
            return column_lookup[candidate.lower()]

    return None


def display_kpis(results, key_prefix):
    """Display KPI cards when the query returns relevant columns."""
    received_col = find_column(
        results,
        ["orders_received", "total_orders_received", "sum_orders_received"],
    )

    delivered_col = find_column(
        results,
        ["orders_delivered", "total_orders_delivered", "sum_orders_delivered"],
    )

    dsr_col = find_column(results, ["dsr_pct"])
    otp_col = find_column(results, ["otp_pct"])

    metrics = []

    if received_col:
        received_total = pd.to_numeric(
            results[received_col], errors="coerce"
        ).sum()
        metrics.append(("Orders received", format_number(received_total)))

    if delivered_col:
        delivered_total = pd.to_numeric(
            results[delivered_col], errors="coerce"
        ).sum()
        metrics.append(("Orders delivered", format_number(delivered_total)))

    if received_col and delivered_col:
        received_total = pd.to_numeric(
            results[received_col], errors="coerce"
        ).sum()
        delivered_total = pd.to_numeric(
            results[delivered_col], errors="coerce"
        ).sum()

        if received_total > 0:
            delivery_rate = delivered_total / received_total * 100
            metrics.append(("Delivery rate", f"{delivery_rate:.2f}%"))

    if dsr_col:
        average_dsr = pd.to_numeric(
            results[dsr_col], errors="coerce"
        ).mean()

        if pd.notna(average_dsr):
            metrics.append(("Average DSR", f"{average_dsr:.2f}%"))

    if otp_col:
        average_otp = pd.to_numeric(
            results[otp_col], errors="coerce"
        ).mean()

        if pd.notna(average_otp):
            metrics.append(("Average OTP", f"{average_otp:.2f}%"))

    if metrics:
        st.markdown("#### Key metrics")

        columns = st.columns(min(len(metrics), 4))

        for index, (label, value) in enumerate(metrics):
            with columns[index % len(columns)]:
                st.metric(label=label, value=value)


def render_visual_analysis(results, message, key_prefix):
    """Render one selected visualization for each individual chat answer."""
    st.markdown("#### Visual analysis")

    button_columns = st.columns(4)
    options = [
        ("bar", "📊 Show Bar Chart"),
        ("line", "📈 Show Line Chart"),
        ("kpi", "🎯 Show KPI Chart"),
        ("explanation", "💡 Show Explanation"),
    ]

    for column, (mode, label) in zip(button_columns, options):
        with column:
            st.button(
                label,
                key=f"visual_{key_prefix}_{mode}",
                type="primary" if message.get("visual_mode") == mode else "secondary",
                use_container_width=True,
                on_click=set_visual_mode,
                args=(st.session_state["active_chat_id"], key_prefix, mode),
            )

    selected_mode = message.get("visual_mode")
    if not selected_mode:
        st.caption("Choose an option above to explore these results.")
        return

    st.divider()

    if selected_mode == "explanation":
        st.markdown("**What this means**")
        st.write(
            message.get("summary")
            or "The query completed. Review the results table and metrics above."
        )
        return

    if results is None or results.empty:
        st.info("There are no result rows to visualize.")
        return

    if selected_mode == "kpi":
        st.markdown("**Key performance indicators**")
        display_kpis(results, key_prefix=f"{key_prefix}_visual_kpi")
        if not any(
            find_column(results, candidates)
            for candidates in [
                ["orders_received", "total_orders_received", "sum_orders_received"],
                ["orders_delivered", "total_orders_delivered", "sum_orders_delivered"],
                ["dsr_pct"],
                ["otp_pct"],
            ]
        ):
            st.info(
                "These results do not contain the supported order or performance "
                "metrics needed to build KPI cards."
            )
        return

    numeric_columns = results.select_dtypes(include="number").columns.tolist()
    numeric_columns = [
        column for column in numeric_columns
        if column.lower() not in {"center_id", "metric_id", "id"}
    ]

    if not numeric_columns:
        st.info("This result does not contain numeric columns for a chart.")
        return

    date_col = find_column(results, ["reporting_date", "date", "order_date"])
    category_col = date_col or find_column(
        results, ["city", "store_code", "status", "delivery_center", "center_name"]
    )

    if category_col is None:
        non_numeric_columns = [
            column for column in results.columns
            if column not in numeric_columns
        ]
        category_col = non_numeric_columns[0] if non_numeric_columns else None

    if category_col is None:
        st.info("A category or date column is needed to build this chart.")
        return

    selected_metric = st.selectbox(
        "Choose a metric",
        options=numeric_columns,
        key=f"visual_metric_{key_prefix}_{selected_mode}",
    )

    chart_data = results[[category_col, selected_metric]].copy()
    chart_data[selected_metric] = pd.to_numeric(
        chart_data[selected_metric], errors="coerce"
    )
    chart_data = chart_data.dropna(subset=[selected_metric])

    if chart_data.empty:
        st.info("There is no numeric data available for this chart.")
        return

    chart_data[category_col] = chart_data[category_col].astype(str)
    chart_data = chart_data.set_index(category_col)

    if selected_mode == "bar":
        st.bar_chart(chart_data[selected_metric])
    elif selected_mode == "line":
        if not date_col:
            st.caption(
                "These results do not include a date column, so the line chart "
                "shows the selected metric across the returned categories."
            )
        st.line_chart(chart_data[selected_metric])


def set_visual_mode(chat_id, message_key, mode):
    """Remember the selected visual for a specific message in a chat."""
    try:
        message_index = int(message_key.rsplit("_", 1)[-1])
        message = st.session_state["chats"][chat_id]["messages"][message_index]
        message["visual_mode"] = mode
    except (KeyError, IndexError, ValueError):
        return


# --------------------------------------------------
# PROCESS A NEW QUESTION
# --------------------------------------------------

pending_question = st.session_state["pending_question"]
st.session_state["pending_question"] = None


if pending_question is not None:
    if not pending_question:
        st.session_state["empty_question_submitted"] = True

    else:
        st.session_state["empty_question_submitted"] = False

        chat_id = st.session_state["active_chat_id"]
        active_chat = st.session_state["chats"][chat_id]

        message = {
            "question": pending_question,
            "sql": None,
            "results": None,
            "summary": None,
            "status": "success",
            "error": None,
            "visual_mode": None,
        }

        try:
            with st.spinner("QueryPilot is analyzing your question..."):

                # Step 1: Retrieve database schema
                start_time = time.perf_counter()
                schema = get_schema()
                print(
                    f"[QueryPilot Timing] Get schema: "
                    f"{time.perf_counter() - start_time:.2f} seconds"
                )

                # Step 2: Generate SQL using Gemini
                start_time = time.perf_counter()
                sql = generate_sql(pending_question, schema)
                print(
                    f"[QueryPilot Timing] SQL generation: "
                    f"{time.perf_counter() - start_time:.2f} seconds"
                )

                if sql == "CANNOT_ANSWER":
                    message["status"] = "cannot_answer"

                else:
                    message["sql"] = sql

                    # Step 3: Execute SQL
                    start_time = time.perf_counter()
                    results = run_generated_query(sql)
                    print(
                        f"[QueryPilot Timing] Database query: "
                        f"{time.perf_counter() - start_time:.2f} seconds"
                    )

                    message["results"] = results

                    # Step 4: Generate AI summary
                    start_time = time.perf_counter()

                    try:
                        summary = generate_summary(
                            pending_question,
                            sql,
                            results,
                        )
                        message["summary"] = summary

                    except Exception:
                        message["summary"] = (
                            "The query completed successfully. "
                            "Please review the results below; "
                            "an AI explanation could not be generated."
                        )

                    finally:
                        print(
                            f"[QueryPilot Timing] Summary generation: "
                            f"{time.perf_counter() - start_time:.2f} seconds"
                        )

        except Exception as error:
            message["status"] = "error"
            message["error"] = str(error)

        active_chat["messages"].append(message)

        # Use the first question as the conversation title.
        if len(active_chat["messages"]) == 1:
            active_chat["title"] = (
                pending_question[:36] + "..."
                if len(pending_question) > 36
                else pending_question
            )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

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

    # Main navigation
    st.page_link(
        "Database_Explorer.py",
        label="Database Explorer",
        icon=":material/database:",
        use_container_width=True,
    )

    st.page_link(
        "pages/1_Upload_Your_Data.py",
        label="Upload Your Data",
        icon=":material/upload_file:",
        use_container_width=True,
    )

    st.divider()

    # New Chat
    st.button(
        "＋ New Chat",
        key="new_chat_button",
        use_container_width=True,
        type="primary",
        on_click=create_new_chat,
    )

    # Chat history
    st.markdown("### Chat history")

    chat_ids = list(st.session_state["chats"].keys())

    for chat_id in reversed(chat_ids):
        chat_title = st.session_state["chats"][chat_id]["title"]
        is_active = (
            chat_id == st.session_state["active_chat_id"]
        )

        label = (
            f"● {chat_title}"
            if is_active
            else f"💬 {chat_title}"
        )

        st.button(
            label,
            key=f"switch_{chat_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            on_click=switch_chat,
            args=(chat_id,),
        )

    st.divider()

    # Suggested questions
    st.markdown("### Try asking")

    st.caption("Which city received the most orders?")
    st.caption("How many orders were delivered in total?")
    st.caption("Show orders received and delivered by city.")
    st.caption("Which city had the lowest OTP?")

    st.divider()

    st.caption("Connected to your QueryPilot database")


# --------------------------------------------------
# MAIN PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero-card">
        <h1>📊 QueryPilot</h1>
        <p><strong>AI-powered Operations Analytics</strong></p>
        <p style="margin-top: 10px; font-size: 1.08rem;">
            QueryPilot — AI-Powered Data Analytics
        </p>
        <p style="margin-top: 6px;">
            Ask questions. Discover insights.
        </p>
        <p style="margin-top: 10px;">
            Ask questions about your operations data in plain English.
            Get SQL, metrics, charts, and AI-generated insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATABASE OVERVIEW AND SUGGESTED QUESTIONS
# --------------------------------------------------

st.markdown("## Explore your operations data")
st.caption(
    "See what's available in the database and discover "
    "questions you can ask in plain English."
)

try:
    overview, center_preview = load_database_overview()

    if not overview.empty:
        row = overview.iloc[0]

        metric_columns = st.columns(3)

        metric_columns[0].metric(
            "Delivery centers",
            f"{int(row['delivery_center_count']):,}",
        )
        metric_columns[1].metric(
            "Daily metric records",
            f"{int(row['metric_record_count']):,}",
        )
        metric_columns[2].metric(
            "Cities",
            f"{int(row['city_count']):,}",
        )

    with st.expander("Preview delivery centers", expanded=False):
        st.dataframe(
            center_preview,
            use_container_width=True,
            hide_index=True,
        )

except Exception:
    st.info(
        "The data overview is temporarily unavailable. "
        "You can still ask questions below."
    )

st.markdown("### Try a suggested question")

suggestions = [
    "How many orders were delivered in total?",
    "How many orders were delivered city wise?",
    "Which city has the highest OTP percentage?",
    "Show orders received and delivered by city.",
    "List all delivery centers by city.",
    "How many delivery centers are open?",
]

suggestion_columns = st.columns(2)

for index, question in enumerate(suggestions):
    with suggestion_columns[index % 2]:
        st.button(
            question,
            key=f"suggested_question_{index}",
            use_container_width=True,
            on_click=set_suggested_question,
            args=(question,),
        )

st.divider()


active_chat_id = st.session_state["active_chat_id"]
active_chat = st.session_state["chats"][active_chat_id]

st.subheader(active_chat["title"])

if not active_chat["messages"]:
    st.info(
        "Start by asking a question below. "
        "Your results will remain visible as you ask more questions."
    )

if st.session_state.get("empty_question_submitted", False):
    st.warning("Please enter a question first.")


# --------------------------------------------------
# RENDER ALL MESSAGES IN THE ACTIVE CHAT
# --------------------------------------------------

for index, message in enumerate(active_chat["messages"]):
    with st.chat_message("user"):
        st.markdown(message["question"])

    with st.chat_message("assistant"):
        if message["status"] == "cannot_answer":
            st.info(
                "I can't answer this question using the available "
                "database tables and columns. Try asking about orders, "
                "cities, dates, or delivery performance."
            )
            continue

        if message["status"] == "error":
            st.error(
                "QueryPilot couldn't complete this request. "
                "Please review the technical details below."
            )

            with st.expander("Technical details"):
                st.code(message["error"] or "Unknown error")

            if message["sql"]:
                with st.expander("Generated SQL"):
                    st.code(message["sql"], language="sql")

            continue

        if message["sql"]:
            with st.expander("View generated SQL", expanded=False):
                st.code(message["sql"], language="sql")

        results = message["results"]

        if results is None:
            st.info("No results are available for this question.")
            continue

        st.markdown("#### Query results")

        if results.empty:
            st.info("No matching records were found.")

        else:
            display_kpis(
                results,
                key_prefix=f"{active_chat_id}_{index}",
            )

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(f"Returned {len(results)} row(s).")

        render_visual_analysis(
            results,
            message,
            key_prefix=f"{active_chat_id}_{index}",
        )

        st.divider()


# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

st.markdown("### Ask another question")

with st.form("question_form", clear_on_submit=False):
    st.text_input(
        "What would you like to know?",
        placeholder="e.g., Which city received the most orders?",
        key="question_input",
    )

    st.form_submit_button(
        "Analyze",
        type="primary",
        use_container_width=True,
        on_click=submit_question,
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "QueryPilot | AI-Powered Data Analytics | "
    "Chat history is currently stored for this app session."
)


