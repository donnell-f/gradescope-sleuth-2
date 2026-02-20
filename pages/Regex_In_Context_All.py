import streamlit as st
from pathlib import Path

from backend.regex.regex_tools import regex_matching_submissions, regex_matching_files
from backend.regex.in_context_matches import get_in_context_matches

st.title("Regex In-Context Matches (All Submissions)")

st.write("Enter a regex pattern and see all places in all files that the pattern matches.")
regex_pattern = st.text_input("Regex Pattern")

if regex_pattern:
    assn_name = st.session_state.get("saved_assn_name")
    if assn_name:
        matching_files_info = regex_matching_files(regex_pattern, assn_name.strip())
        if matching_files_info:
            all_in_context_matches = ""

            # Iterate through matched files to get in-context matches
            match_number = 1
            # DB will return:
            # st.uin, st.name, st.email, s.submission_id, s.created_at, s.score, s.submission_num, f.file_name, f.file_text
            for st_uin, st_name, st_email, s_sub_id, s_created_at, s_score, s_sub_num, f_name, f_text in matching_files_info:
                
                f_in_context_matches = get_in_context_matches(
                    pattern=regex_pattern,
                    file_name=f_name,
                    file_text=f_text,
                    student_name=st_name,
                    uin=st_uin,
                    email=st_email,
                    match_number_enabled=False,    # Maybe use these options later?
                    match_number=match_number,
                    case_sensitive=True,
                    context_radius=1
                )

                match_number += 1

                # Append the in context matches for this file to the total all_in_context_matches string
                all_in_context_matches += f_in_context_matches + "\n\n"
                
            st.code(all_in_context_matches, language=None)
        else:
            st.info("No submissions matched the given pattern.")
    else:
        st.error("No assignment configured. Please complete configuration first.")