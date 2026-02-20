import streamlit as st
import sqlite3
from pathlib import Path

EXT_TO_LANG = {
    ".py": "python",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".h": "cpp", ".hpp": "cpp",
    ".c": "c",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".java": "java",
    ".cs": "csharp",
    ".go": "go",
    ".sql": "sql",
    ".sh": "bash", ".bash": "bash",
    ".html": "html",
    ".json": "json",
    ".yml": "yaml", ".yaml": "yaml",
}

st.title("Print History")
st.write("Prints the submission history of a student. Students can be identified by either their name, their UIN, or their email.")

id_method = st.radio("Identify student by:", ["Name", "UIN", "Email"])

student_identifier = None
if id_method == "Name":
    student_identifier = st.text_input("Student Name")
elif id_method == "UIN":
    student_identifier = st.number_input("Student UIN", min_value=0, value=0, step=1)
elif id_method == "Email":
    student_identifier = st.text_input("Student Email")

# Only proceed if the user has entered something
should_search = (id_method == "UIN" and student_identifier > 0) or \
                (id_method != "UIN" and student_identifier)

if should_search:
    assn_name = st.session_state.get("saved_assn_name")
    if not assn_name:
        st.error("No assignment configured. Please complete configuration first.")
    else:
        db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        # Find the student
        if id_method == "Name":
            curs.execute("SELECT uin, name, email FROM students WHERE name = ?", (student_identifier,))
        elif id_method == "UIN":
            curs.execute("SELECT uin, name, email FROM students WHERE uin = ?", (int(student_identifier),))
        elif id_method == "Email":
            curs.execute("SELECT uin, name, email FROM students WHERE email = ?", (student_identifier,))

        student = curs.fetchone()

        if not student:
            curs.close()
            conn.close()
            st.error(f"No student found with {id_method.lower()}: {student_identifier}")
        else:
            stu_uin, stu_name, stu_email = student
            st.write("")
            st.write(f"**Student:** {stu_name} | **UIN:** {stu_uin} | **Email:** {stu_email}")
            st.divider()

            # Get all submissions that have files in the files table
            curs.execute("""
                SELECT DISTINCT s.submission_id, s.created_at, s.score, s.submission_num
                FROM submissions s
                JOIN files f ON s.submission_id = f.submission_id
                WHERE s.uin = ?
                ORDER BY s.created_at DESC
            """, (stu_uin,))
            submissions = curs.fetchall()

            if not submissions:
                st.info("No submissions with files found for this student.")
            else:
                for sub_id, created_at, score, sub_num in submissions:
                    st.write(f"**Submission #{sub_num}** — ID: {sub_id} | Created: {created_at} | Score: {score}")

                    # Get all files for this submission
                    curs.execute("""
                        SELECT file_name, file_text
                        FROM files
                        WHERE submission_id = ?
                    """, (sub_id,))
                    files = curs.fetchall()

                    for file_name, file_text in files:
                        ext = Path(file_name).suffix.lower()
                        lang = EXT_TO_LANG.get(ext)
                        with st.expander(f"📄 {file_name}"):
                            st.code(file_text, language=lang)

                    st.divider()

            curs.close()
            conn.close()
