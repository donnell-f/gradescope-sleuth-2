import streamlit as st

st.set_page_config(
    page_title="Gradescope Sleuth",
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

st.sidebar.title("Gradescope Sleuth")

# Hide the deploy button and hamburger menu
st.markdown(
    """
    <style>
        .stMainMenu {visibility: hidden;}
        .stAppDeployButton {display: none;}
        [data-testid="stSidebarCollapseButton"] {display: none;}
        section[data-testid="stSidebar"] {width: 250px !important; min-width: 250px !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Dynamic page navigation ---
config_page = st.Page("pages/Config.py", title="Config", default=True)
regex_list_page = st.Page("pages/Regex_List.py", title="Regex List")
regex_in_context_page = st.Page("pages/Regex_In_Context.py", title="Regex In Context")
about_config_page = st.Page("pages/About_Configuration.py", title="About Configuration")

pages = [config_page, regex_list_page, about_config_page]
nav = st.navigation(pages, position="hidden")

# Manually render sidebar links based on setup state
if not st.session_state.get("setup_complete"):
    st.sidebar.page_link(config_page, label="Config")
else:
    st.sidebar.page_link(regex_list_page, label="Regex List Submissions")
    st.sidebar.page_link(regex_list_page, label="Regex In Context Matches")
    st.sidebar.page_link(about_config_page, label="About Configuration")

nav.run()
