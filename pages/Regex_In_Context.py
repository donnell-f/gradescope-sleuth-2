import streamlit as st
import pandas as pd

from backend.regex.regex_tools import regex_matching_submissions, regex_matching_files
from backend.regex.in_context_matches import get_in_context_matches

st.title("Regex In-Context Matches")

st.write("### Regex In-content Matches")
st.write("Enter a regex pattern and see all places in all files that the pattern matches.")
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