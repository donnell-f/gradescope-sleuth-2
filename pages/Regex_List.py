import streamlit as st
import pandas as pd

from backend.regex.regex_tools import regex_matching_submissions, regex_matching_student_submissions

st.title("Regex List Submissions")

st.write("Enter a regex pattern and see a table of all submissions with files matching the pattern.")
regex_pattern = st.text_input("Regex Pattern")

first_only = st.toggle("Select only the first matching submission per student?", value=False)

if regex_pattern:
    assn_name = st.session_state.get("saved_assn_name")
    if assn_name:
        if first_only:
            columns, rows = regex_matching_student_submissions(regex_pattern, assn_name.strip())
        else:
            columns, rows = regex_matching_submissions(regex_pattern, assn_name.strip())
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df)
        else:
            st.info("No submissions matched the given pattern.")
    else:
        st.error("No assignment configured. Please complete configuration first.")



