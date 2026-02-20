import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import threading
import time
from datetime import datetime
import os
from pathlib import Path
import json

from backend.configuration.configure_new_database import configure_new_database
from backend.configuration.configuration_helpers import clear_config_dir

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

past_configs = [f for f in os.listdir("./configs") if os.path.isdir(os.path.join("./configs", f))]

# If loading previous configuration
if (mode == "Load existing configuration"):

    past_config_select = st.selectbox("Select an existing configuration",
                 index=None,    # So that the placeholder shows
                 placeholder="Select a past config file...",
                 options=past_configs)

    if past_config_select != None:
        try:
            # Load the config dict
            past_config_path = Path(".") / "configs" / past_config_select / f"{past_config_select}.config.json"
            with open(past_config_path, "r") as f:
                config_dict = json.loads(f.read())

            # Turn datetime strings into actual datetimes
            config_dict["due_date"] = datetime.strptime(config_dict["due_date"], "%Y-%m-%d %H:%M:%S")
            if "late_due_date" in config_dict:
                config_dict["late_due_date"] = datetime.strptime(config_dict["late_due_date"], "%Y-%m-%d %H:%M:%S")

            # Load the config_dict data into their respective session states 
            st.session_state["saved_assn_name"] = config_dict["assignment_name"]
            st.session_state["saved_assn_path"] = config_dict["assignment_path"]
            st.session_state["saved_due_date"] = config_dict["due_date"]
            st.session_state["saved_has_late_due_date"] = config_dict.get("has_late_due_date", "No")
            st.session_state["saved_late_due_date"] = config_dict.get("late_due_date")
            st.session_state["saved_has_network_settings"] = config_dict.get("has_network_settings", "No")
            if config_dict.get("has_network_settings") == "Yes":
                st.session_state["saved_course_id"] = config_dict.get("course_id")
                st.session_state["saved_assignment_id"] = config_dict.get("assignment_id")
                st.session_state["saved_remember_me_cookie"] = config_dict.get("remember_me_cookie")
                st.session_state["saved_signed_token_cookie"] = config_dict.get("signed_token_cookie")

            if not st.session_state.get("setup_complete"):
                st.session_state["setup_complete"] = True
                st.rerun()

            st.success("Configuration complete! Proceed to any other page to use the app.")
        except Exception as e:
            st.error(f"Error: could not load specified config. Details: {e}")
    

# If creating new configuration
else:
    # ----- Get config info ----- #

    # Enter name for current assignment
    assn_name = st.text_input('Please enter a name for this assignment configuration (no spaces " ", nor forward slashes "/", nor backslashes "\\")', value="", key="assn_name")
    assn_exists = assn_name.strip() in past_configs and not (st.session_state["config_running"] or st.session_state["config_done"])
    if " " in assn_name or "/" in assn_name or "\\" in assn_name:
        st.error("Assignment name cannot contain spaces or forward slashes.")
    if assn_exists:
        st.error("There is already a saved assignment configuration with that name. Please delete it or choose a different name.")

    # Enter path to assignment folder
    assn_path = st.text_input("Please enter the absolute path to the downloaded submissions folder (e.g. /home/username/csce120_downloaded_submissions)", value="", key="assn_path")

    # Enter the due date for current assignment
    due_date = st.datetime_input("Please enter the due date for this assignment", value="now", key="due_date")

    # Enter late due date (if applicable)
    has_late_due_date = st.radio("Does this assignment have a late due date?", ["No", "Yes"], key="has_late_due_date")
    if (has_late_due_date == "Yes"):
        late_due_date = st.datetime_input("Please enter the LATE due date for this assignment", value="now", key="late_due_date")
    
    # Network settings for downloading solutions
    has_network_settings = st.radio("Do you want to configure network settings for downloading solutions?", ["No", "Yes"], key="has_network_settings")
    if has_network_settings == "Yes":
        course_id = st.number_input("Course ID", min_value=0, value=0, step=1, key="course_id")
        assignment_id = st.number_input("Assignment ID", min_value=0, value=0, step=1, key="assignment_id")
        remember_me_cookie = st.text_input("remember_me cookie", value="", key="remember_me_cookie")
        signed_token_cookie = st.text_input("signed_token cookie", value="", key="signed_token_cookie")


    # ----- Validate config info ----- #

    # `any_fields_invalid` is boolean a variable for start_config_button
    assn_name_invalid = (" " in assn_name) or ("/" in assn_name) or ("\\" in assn_name) or assn_exists
    any_fields_invalid = assn_name.strip() == "" or assn_path.strip() == "" or due_date == None or assn_name_invalid

    is_running = st.session_state["config_running"]

    # Status message
    if is_running:
        st.info("Configuration is running... This may take 10 - 25 minutes, depending on your hardware.")
    elif st.session_state.get("config_was_cancelled"):
        st.warning("Configuration was cancelled.")
    elif st.session_state["config_done"]:
        st.success("Configuration complete! Proceed to any other page to use the app.")

    # ----- Start configuration process ----- #

    # Both buttons always visible, enabled/disabled based on state
    col1, col2 = st.columns(2)
    with col1:
        if col1.button("Start Config", disabled=any_fields_invalid or is_running):
            st.session_state["config_cancelled"].clear()
            st.session_state["config_running"] = True
            st.session_state["config_done"] = False
            st.session_state["config_was_cancelled"] = False

            # Save config values to persistent (non-widget) keys
            # Streamlit is really weird about session state...
            st.session_state["saved_assn_name"] = st.session_state["assn_name"]
            st.session_state["saved_assn_path"] = st.session_state["assn_path"]
            st.session_state["saved_due_date"] = st.session_state["due_date"]
            st.session_state["saved_has_late_due_date"] = st.session_state["has_late_due_date"]
            st.session_state["saved_late_due_date"] = st.session_state.get("late_due_date")
            st.session_state["saved_has_network_settings"] = st.session_state["has_network_settings"]
            if st.session_state["has_network_settings"] == "Yes":
                st.session_state["saved_course_id"] = st.session_state["course_id"]
                st.session_state["saved_assignment_id"] = st.session_state["assignment_id"]
                st.session_state["saved_remember_me_cookie"] = st.session_state["remember_me_cookie"]
                st.session_state["saved_signed_token_cookie"] = st.session_state["signed_token_cookie"]

            # Depositing this state into a variable since it is a `threading` event
            cancel_event = st.session_state["config_cancelled"]

            # Run the database configuration function in this thread
            def run_config():
                try:
                    success = configure_new_database(
                        cancel_event,
                        assn_name=st.session_state["assn_name"].strip(),    # Strip it
                        assn_path=Path(st.session_state["assn_path"].strip()),    # Strip it and Path() it
                        due_date=st.session_state["due_date"],
                        has_late_due_date=st.session_state["has_late_due_date"],
                        late_due_date=st.session_state.get("late_due_date"),
                        has_network_settings=st.session_state["has_network_settings"],
                        course_id=st.session_state.get("course_id"),
                        assignment_id=st.session_state.get("assignment_id"),
                        remember_me_cookie=st.session_state.get("remember_me_cookie"),
                        signed_token_cookie=st.session_state.get("signed_token_cookie"),
                    )
                    if success:
                        # Show "config done" message on successful completion
                        st.session_state["config_done"] = True
                        st.session_state["setup_complete"] = True
                    else:
                        # Clear the config directory if the user cancelled configuration
                        clear_config_dir(assn_name.strip())
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

