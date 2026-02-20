import sqlite3
import os
from pathlib import Path

from backend.regex.sqlite_regex_backend import py_regexp_csensitive


def regex_matching_submissions(regex_pattern: str, assn_name: str):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)    # Add REGEXP command
    curs = conn.cursor()

    curs.execute("""
        SELECT DISTINCT s.submission_id, s.created_at, s.score, s.submission_num,
               st.uin, st.name, st.email
        FROM files f
        JOIN submissions s ON f.submission_id = s.submission_id
        JOIN students st ON s.uin = st.uin
        WHERE f.file_text REGEXP ?
    """, (regex_pattern,))

    rows = curs.fetchall()
    columns = [desc[0] for desc in curs.description]

    curs.close()
    conn.close()

    return columns, rows

def regex_matching_files(regex_pattern: str, assn_name: str):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)    # Add REGEXP command
    curs = conn.cursor()

    curs.execute("""
        SELECT st.uin, st.name, st.email, s.submission_id,
               s.created_at, s.score, s.submission_num, f.file_name, f.file_text
        FROM files f
        JOIN submissions s ON f.submission_id = s.submission_id
        JOIN students st ON s.uin = st.uin
        WHERE f.file_text REGEXP ?
    """, (regex_pattern,))

    matching_files = curs.fetchall()

    curs.close()
    conn.close()

    return matching_files

