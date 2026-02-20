import streamlit as st

st.set_page_config(
    page_title="Gradescope Sleuth 🫆",
    page_icon="🫆",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a Bug": None,
        "About": None,
    }
)

if "setup_complete" not in st.session_state:
    st.session_state["setup_complete"] = False

st.sidebar.title("Gradescope Sleuth 🫆")

# Hide the deploy button and hamburger menu
st.markdown(
    """
    <style>
        .stMainMenu {visibility: hidden;}
        .stAppDeployButton {display: none;}
        [data-testid="stSidebarCollapseButton"] {display: none;}
        section[data-testid="stSidebar"] {min-width: 20rem !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Dynamic page navigation ---
config_page = st.Page("pages/Config.py", title="Config", default=True)
regex_list_page = st.Page("pages/Regex_List.py", title="Regex List Submissions")
regex_in_context_all_page = st.Page("pages/Regex_In_Context_All.py", title="Regex In Context (All)")
regex_in_context_one_page = st.Page("pages/Regex_In_Context_One.py", title="Regex In Context (One)")
print_history_page = st.Page("pages/Print_History.py", title="Print History")
download_historical_all_page = st.Page("pages/Download_Historical_All.py", title="Download Historical (All)")
download_historical_one_page = st.Page("pages/Download_Historical_One.py", title="Download Historical (One)")
about_config_page = st.Page("pages/About_Configuration.py", title="About Configuration")

pages = [config_page, regex_list_page, regex_in_context_all_page, regex_in_context_one_page, print_history_page, download_historical_all_page, download_historical_one_page, about_config_page]
nav = st.navigation(pages, position="hidden")

# Manually render sidebar links based on setup state
if not st.session_state.get("setup_complete"):
    st.sidebar.page_link(config_page, label="Config")
else:
    st.sidebar.page_link(regex_list_page, label="Regex List Submissions")
    st.sidebar.page_link(regex_in_context_all_page, label="Regex In Context Matches (All)")
    st.sidebar.page_link(regex_in_context_one_page, label="Regex In Context Matches (One)")
    st.sidebar.page_link(print_history_page, label="Print History")
    st.sidebar.page_link(download_historical_all_page, label="Download Historical (All)")
    st.sidebar.page_link(download_historical_one_page, label="Download Historical (One)")
    st.sidebar.page_link(about_config_page, label="About Configuration")

nav.run()
