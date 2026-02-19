import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import threading
import time
import os
from pathlib import Path

from backend.configure_database import configure_database

st.title("Config Page")

# Initialize config state
if "config_running" not in st.session_state:
    st.session_state["config_running"] = False
if "config_cancelled" not in st.session_state:
    st.session_state["config_cancelled"] = threading.Event()
if "config_done" not in st.session_state:
    st.session_state["config_done"] = False

st.write("Welcome to Gradescope Sleuth! This page will walk you through the Gradescope Sleuth configuration process.")

mode = st.radio("How would you like to configure Gradescope Sleuth?", ["Load existing configuration", "Create new"])

past_configs = [f for f in os.listdir("./configs_archive") if os.path.isdir(os.path.join("./configs_archive", f))]

# If loading previous configuration
if (mode == "Load existing configuration"):

    past_config_select = st.selectbox("Select an existing configuration",
                 index=None,    # So that the placeholder shows
                 placeholder="Select a past config file...",
                 options=past_configs)
    print(st.session_state["setup_complete"])

    if past_config_select != None and not st.session_state.get("setup_complete"):
        st.session_state["setup_complete"] = True
        st.rerun()    # Rerun to make sure session_state updates

# If creating new configuration
else:
    # Enter name for current assignment
    assn_name = st.text_input('Please enter a name for this assignment (no spaces " " or forward slashes "/")', value="", key="assn_name")
    if " " in assn_name or "/" in assn_name:
        st.error("Assignment name cannot contain spaces or forward slashes.")
    if assn_name.strip() in past_configs:
        st.error("There is already a saved assignment configuration with that name. Please delete it or choose a different name.")

    # Enter path to assignment folder
    assn_path = st.text_input("Please enter the absolute path to the downloaded submissions folder (e.g. /home/username/csce120_downloaded_submissions)", value="", key="assn_path")

    # Enter the due date for current assignment
    due_date = st.datetime_input("Please enter the due date for this assignment", value="now", key="due_date")

    # Enter late due date (if applicable)
    has_late_due_date = st.radio("Does this assignment have a late due date?", ["No", "Yes"], key="has_late_due_date")
    if (has_late_due_date == "Yes"):
        late_due_date = st.datetime_input("Please enter the LATE due date for this assignment", value="now", key="late_due_date")

    # `any_fields_invalid` is boolean a variable for start_config_button
    assn_name_invalid = (" " in assn_name) or ("/" in assn_name) or (assn_name.strip() in past_configs)
    any_fields_invalid = assn_name.strip() == "" or assn_path.strip() == "" or due_date == None or assn_name_invalid

    is_running = st.session_state["config_running"]

    # Status message
    if is_running:
        st.info("Configuration is running...")
    elif st.session_state.get("config_was_cancelled"):
        st.warning("Configuration was cancelled.")
    elif st.session_state["config_done"]:
        st.success("Configuration complete! Proceed to the Dashboard page to use the app.")

    # Both buttons always visible, enabled/disabled based on state
    col1, col2 = st.columns(2)
    with col1:
        if col1.button("Start Config", disabled=any_fields_invalid or is_running):
            st.session_state["config_cancelled"].clear()
            st.session_state["config_running"] = True
            st.session_state["config_done"] = False
            st.session_state["config_was_cancelled"] = False

            # Save config values to persistent (non-widget) keys
            st.session_state["saved_assn_name"] = st.session_state["assn_name"]
            st.session_state["saved_assn_path"] = st.session_state["assn_path"]
            st.session_state["saved_due_date"] = st.session_state["due_date"]
            st.session_state["saved_has_late_due_date"] = st.session_state["has_late_due_date"]
            st.session_state["saved_late_due_date"] = st.session_state.get("late_due_date")

            # Depositing this state into a variable since it is a `threading` event
            cancel_event = st.session_state["config_cancelled"]

            # Run the database configuration function in this thread
            def run_config():
                try:
                    success = configure_database(
                        cancel_event,
                        assn_name=st.session_state["assn_name"].strip(),    # Strip it
                        assn_path=Path(st.session_state["assn_path"].strip()),    # Strip it and Path() it
                        due_date=st.session_state["due_date"],
                        has_late_due_date=st.session_state["has_late_due_date"],
                        late_due_date=st.session_state.get("late_due_date"),
                    )
                    if success:
                        st.session_state["config_done"] = True
                        st.session_state["setup_complete"] = True
                finally:
                    st.session_state["config_running"] = False

            thread = threading.Thread(target=run_config, daemon=True)
            add_script_run_ctx(thread)
            thread.start()
            st.rerun()
    with col2:
        if col2.button( "Cancel", disabled=(not is_running) ):
            st.session_state["config_cancelled"].set()
            st.session_state["config_running"] = False
            st.session_state["config_done"] = False
            st.session_state["config_was_cancelled"] = True
            st.rerun()

    # Poll while running
    if is_running:
        time.sleep(0.5)
        st.rerun()

