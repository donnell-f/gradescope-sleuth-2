import streamlit as st
from pathlib import Path
import sqlite3

from backend.regex.regex_tools import regex_matching_submissions, regex_matching_files
from backend.regex.in_context_matches import get_in_context_matches

st.title("Regex In-Context Matches (One Submission)")

st.write("Enter a regex pattern and a submission ID to find in context matches for all files in that *one* submission.")
regex_pattern = st.text_input("Regex Pattern")
submission_id = st.number_input("Submission ID", min_value=0, value=0, step=1)


if regex_pattern and submission_id > 0:
    assn_name = st.session_state.get("saved_assn_name")
    # assn_path = st.session_state.get("saved_assn_path")
    if assn_name:
        db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        # Get the files for submission with `submission_id`
        curs.execute("""
            SELECT st.uin, st.name, st.email, s.submission_id, s.created_at, s.score, s.submission_num, f.file_name, f.file_text
            FROM files f
            JOIN submissions s ON f.submission_id = s.submission_id
            JOIN students st ON s.uin = st.uin
            WHERE s.submission_id = ?
        """, (int(submission_id),))
        matching_files = curs.fetchall()

        curs.close()
        conn.close()

        if matching_files:
            all_in_context_matches = ""

            # Iterate through matched files to get in-context matches
            match_number = 1
            # DB will return:
            # st.uin, st.name, st.email, s.submission_id, s.created_at, s.score, s.submission_num, f.file_name, f.file_text
            for st_uin, st_name, st_email, s_sub_id, s_created_at, s_score, s_sub_num, f_name, f_text in matching_files:
                
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
            st.info(f"No files in submission {submission_id} matched the given pattern.")
    else:
        st.error("No assignment configured. Please complete configuration first.")