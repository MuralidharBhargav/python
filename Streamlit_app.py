import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Data Quality Control Center",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Inject Custom CSS to clean sidebar ---
st.markdown(
    """
    <style>
    .streamlit-expander {
        border: none;
        box-shadow: none;
        background-color: transparent;
    }
    .streamlit-expanderHeader {
        background-color: transparent;
        font-weight: bold;
        padding-left: 5px;
    }
    button[kind="secondary"] {
        border: none;
        box-shadow: none;
        background-color: transparent;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.image("https://via.placeholder.com/150", width=150)  # Optional logo

selected_page = None

# Top Level Navigation
if st.sidebar.button("🏠 Overview"):
    selected_page = "Overview"

# Metadata Section
with st.sidebar.expander("📂 Metadata", expanded=False):
    if st.button("🔍 Explorer", key="meta_explorer"):
        selected_page = "Metadata Explorer"
    if st.button("🧬 Lineage", key="meta_lineage"):
        selected_page = "Metadata Lineage"

# Data Quality Section
with st.sidebar.expander("🛡️ Data Quality", expanded=False):
    if st.button("📈 Summary", key="dq_summary"):
        selected_page = "Data Quality Summary"
    if st.button("📋 Details", key="dq_details"):
        selected_page = "Data Quality Details"

# Workflow Section
with st.sidebar.expander("🔧 Workflow", expanded=False):
    if st.button("📝 Issue Details", key="workflow_issue"):
        selected_page = "Workflow Issue Details"
    if st.button("🛠️ Remediation", key="workflow_remediation"):
        selected_page = "Workflow Remediation"

# Logout
st.sidebar.markdown("---")
st.sidebar.button("Logout")

# --- Main Page Content based on selected_page ---

# If nothing selected, default to Overview
if selected_page is None:
    selected_page = "Overview"

# --- Overview Page ---
if selected_page == "Overview":
    # Main Heading
    st.markdown("<h1 style='text-align: center; font-size: 48px;'>Data Quality Control Center</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 20px;'>Monitor and manage your data assets with confidence</p>",
        unsafe_allow_html=True)
    st.markdown("")

    # Search Bar
    search_query = st.text_input(" ", placeholder="Type here to Explore a Data Asset...", key="search_bar")

    # KPIs - Metrics Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Data Assets", value="1842", delta="+400 (22%)")
    with col2:
        st.metric(label="Active Issues", value="23", delta="-10 less than yesterday")
    with col3:
        st.metric(label="Assets Monitored", value="1658", delta="90% coverage")

    st.markdown("---")

    # Quick Actions Section
    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("🔍 View Metadata")
    with col2:
        st.button("🛠️ Check Data Quality")
    with col3:
        st.button("⚠️ Report Issue")

    st.markdown("---")

    # Recent Activity Section
    st.subheader("Recent Activity")

    recent_activity_data = {
        "Time": ["10 min ago", "1 hour ago", "Yesterday"],
        "Asset": ["Customer Database", "Sales Records", "Inventory"],
        "Action": ["Quality Check", "Metadata Update", "Issue Reported"],
        "Status": ["Passed", "Updated", "Open"],
    }

    df = pd.DataFrame(recent_activity_data)

    # Build the table manually with colored status
    for i in range(len(df)):
        cols = st.columns((1, 2, 2, 1))
        cols[0].markdown(df["Time"][i])
        cols[1].markdown(df["Asset"][i])
        cols[2].markdown(df["Action"][i])

        status = df["Status"][i]
        color = "green" if status == "Passed" else "orange" if status == "Updated" else "red"
        cols[3].markdown(
            f"<div style='background-color:{color};padding:5px;border-radius:5px;text-align:center;color:white'>{status}</div>",
            unsafe_allow_html=True
        )

# --- Other Pages ---
elif selected_page == "Metadata Explorer":
    st.title("📂 Metadata - Explorer")
    st.info("Explore your metadata assets here.")

elif selected_page == "Metadata Lineage":
    st.title("📂 Metadata - Lineage")
    st.info("Visualize the full lineage from source to consumption.")

elif selected_page == "Data Quality Summary":
    st.title("🛡️ Data Quality - Summary")
    st.info("Summary of all data quality checks across assets.")

elif selected_page == "Data Quality Details":
    st.title("🛡️ Data Quality - Details")
    st.info("Detailed quality metrics and checks for data assets.")

elif selected_page == "Workflow Issue Details":
    st.title("🔧 Workflow - Issue Details")
    st.info("Reported issues on datasets.")

elif selected_page == "Workflow Remediation":
    st.title("🔧 Workflow - Remediation")
    st.info("Manage remediation activities for reported issues.")
