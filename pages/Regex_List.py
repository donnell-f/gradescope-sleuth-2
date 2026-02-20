import streamlit as st
import pandas as pd

from backend.regex.regex_tools import regex_matching_submissions

st.title("Regex List Submissions")

st.write("Enter a regex pattern and see a table of all submissions with files matching the pattern.")
regex_pattern = st.text_input("Regex Pattern")

if regex_pattern:
    assn_name = st.session_state.get("saved_assn_name")
    if assn_name:
        columns, rows = regex_matching_submissions(regex_pattern, assn_name.strip())
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df)
        else:
            st.info("No submissions matched the given pattern.")
    else:
        st.error("No assignment configured. Please complete configuration first.")



