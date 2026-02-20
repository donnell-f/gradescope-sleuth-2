import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import threading
import time
import pandas as pd

from backend.downloading.downloading import download_submission_as_dict
from backend.downloading.sql_helpers import (
    get_submissions_with_download_status,
    get_undownloaded_submission_ids,
    insert_downloaded_files,
)

st.title("Download Historical Submissions (All)")
st.write("Downloads all historical submission files from Gradescope for submissions that are in the database but don't have files stored locally yet. Network settings must be configured on the Config page.")

# Initialize download state
if "dl_running" not in st.session_state:
    st.session_state["dl_running"] = False
if "dl_cancelled" not in st.session_state:
    st.session_state["dl_cancelled"] = threading.Event()
if "dl_done" not in st.session_state:
    st.session_state["dl_done"] = False
if "dl_error" not in st.session_state:
    st.session_state["dl_error"] = None

assn_name = st.session_state.get("saved_assn_name")

if not assn_name:
    st.error("No assignment configured. Please complete configuration first.")
elif st.session_state.get("saved_has_network_settings") != "Yes":
    st.error("Network settings are not configured. Please reconfigure the assignment with network settings enabled.")
else:
    course_id = st.session_state.get("saved_course_id")
    assignment_id = st.session_state.get("saved_assignment_id")
    remember_me = st.session_state.get("saved_remember_me_cookie")
    signed_token = st.session_state.get("saved_signed_token_cookie")

    is_running = st.session_state["dl_running"]

    # Status messages
    if is_running:
        st.info("Downloading in progress...")
    elif st.session_state.get("dl_was_cancelled"):
        st.warning("Downloading was stopped.")
    elif st.session_state.get("dl_error"):
        st.error(f"Download stopped due to an error: {st.session_state['dl_error']}")
    elif st.session_state["dl_done"]:
        st.success("All submissions have been downloaded!")

    # Start / Stop buttons
    col1, col2 = st.columns(2)
    with col1:
        if col1.button("Start Downloading", disabled=is_running):
            # Set session states appropriately to incidate active downloading
            st.session_state["dl_cancelled"].clear()
            st.session_state["dl_running"] = True
            st.session_state["dl_done"] = False
            st.session_state["dl_error"] = None
            st.session_state["dl_was_cancelled"] = False

            # Save this in here for convenience
            cancel_event = st.session_state["dl_cancelled"]

            # The downloading function -- to be run in a thread
            # NOTE:
            def run_downloads():
                try:
                    undownloaded = get_undownloaded_submission_ids(assn_name)
                    for sub_id in undownloaded:
                        if cancel_event.is_set():
                            return

                        # Downloads the submission .zip from Gradescope and
                        # returns it as a dictionary mapping file names -> file content.
                        files_dict = download_submission_as_dict(
                            course_id=course_id,
                            assn_id=assignment_id,
                            submission_id=sub_id,
                            remember_me=remember_me,
                            signed_token=signed_token,
                        )
                        insert_downloaded_files(assn_name, sub_id, files_dict)

                    if not cancel_event.is_set():
                        st.session_state["dl_done"] = True
                except Exception as e:
                    st.session_state["dl_error"] = str(e)
                finally:
                    st.session_state["dl_running"] = False

            thread = threading.Thread(target=run_downloads, daemon=True)
            add_script_run_ctx(thread)
            thread.start()
            st.rerun()
    with col2:
        if col2.button("Stop", disabled=not is_running):
            st.session_state["dl_cancelled"].set()
            st.session_state["dl_running"] = False
            st.session_state["dl_was_cancelled"] = True
            st.rerun()

    # Show the submissions table only while running or after completion
    if is_running or st.session_state["dl_done"]:
        # Streamlit will auto-update the dataframe, which makes my life 1000x easier.
        columns, rows = get_submissions_with_download_status(assn_name)
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No submissions found in the database.")

    # Poll while running to refresh the table
    if is_running:
        time.sleep(1)
        st.rerun()
