import streamlit as st
import pandas as pd

# Page setup - MUST be the first Streamlit command
st.set_page_config(page_title="Data Quality Control Center", layout="wide")

# Custom CSS for centering placeholder text
st.markdown("""
    <style>
        input::placeholder {
            text-align: center;
        }
        input {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Main dashboard content
st.markdown("""
    <h2 style="text-align: center;">Data Quality Control Center</h2>
""", unsafe_allow_html=True)

# Custom subheader with reduced font size
st.markdown("""
    <h4 style="text-align: center; font-size: 16px;">Monitor and manage your data assets with confidence</h4>
""", unsafe_allow_html=True)

# Search Bar at the top
search_query = st.text_input(" ", placeholder="Type here to Explore a Data Asset...")
if search_query:
    st.write(f"Searching for: {search_query}")

# Adding blank lines using st.write
st.write("")

# Adding blank lines using st.markdown
#st.markdown("<br><br>", unsafe_allow_html=True)

# Remaining content...
# Custom CSS for theming and fonts
st.markdown("""
    <style>
        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
        }

        /* Main page background */
        div[data-testid="stAppViewContainer"] > .main {
            background-color: #000000; /* White background */
            color: #f5f5f5; /* Black font color */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #000000;
        }

        /* Metric font */
        div[data-testid="metric-container"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }

        /* Button style */
        button[kind="primary"] {
            font-weight: bold;
        }

        /* Table font */
        .stDataFrame div {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    </style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.image("https://placehold.co/50x50", caption="logo")
    st.markdown("### MAIN")
    selection = st.radio("", ["Dashboard", "Team"], index=0)
    st.markdown("### SETTINGS")
    if st.button("Logout"):
        st.write("Logged out")

# Main dashboard content
#st.title("Data Discovery & Quality Management")
#st.subheader("Monitor and manage your data assets with confidence")

# Metrics
col1, col3, col4 = st.columns(3)

col1.metric("Total Data Assets", "1842", "400 (22%)")
#col2.metric("Business Processes", "5", "2 more than last month")
col3.metric("Active Issues", "23", "10 less than yesterday")
col4.metric("Assets Monitored", "1658", "90% coverage")

st.divider()

# Quick Actions
st.markdown("#### Quick Actions")
action_col1, action_col2, action_col3 = st.columns([1, 1, 1])
with action_col1:
    if st.button("🔍 View Metadata"):
        st.write("Viewing metadata...")
with action_col2:
    if st.button("📈 Check Data Quality"):
        st.write("Checking data quality...")
with action_col3:
    if st.button("⚠️ Report Issue"):
        st.write("Reporting an issue...")

st.write("")

# Recent Activity
st.markdown("#### Recent Activity")
data = pd.DataFrame({
    "Time": ["10 min ago", "1 hour ago", "Yesterday"],
    "Asset": ["Customer Database", "Sales Records", "Inventory"],
    "Action": ["Quality Check", "Metadata Update", "Issue Reported"],
    "Status": ["Passed", "Updated", "Open"]
})

def color_status(val):
    color = "green" if val == "Passed" else "orange" if val == "Updated" else "red"
    return f"background-color: {color}; color: white"

styled_df = data.style.applymap(color_status, subset=['Status'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)
