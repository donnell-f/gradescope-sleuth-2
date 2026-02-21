import sqlite3
from pathlib import Path


def get_submissions_with_download_status(assn_name: str):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    curs.execute("""
        SELECT s.submission_id, s.score, s.submission_num,
               s.uin, st.name AS student_name,
               CASE WHEN COUNT(f.file_id) > 0 THEN '✅' ELSE '🚫' END AS is_downloaded
        FROM submissions s
        JOIN students st ON s.uin = st.uin
        LEFT JOIN files f ON s.submission_id = f.submission_id
        GROUP BY s.submission_id
        ORDER BY student_name
    """)

    rows = curs.fetchall()
    columns = [desc[0] for desc in curs.description]

    curs.close()
    conn.close()

    return columns, rows


def get_undownloaded_submission_ids(assn_name: str):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    curs.execute("""
        SELECT s.submission_id, st.name
        FROM submissions s
        JOIN students st ON s.uin = st.uin
        LEFT JOIN files f ON s.submission_id = f.submission_id
        WHERE f.file_id IS NULL
        ORDER BY st.name, s.submission_num
    """)

    rows = curs.fetchall()

    curs.close()
    conn.close()

    return rows


def get_submissions_with_download_status_by_uin(assn_name: str, uin: int):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    curs.execute("""
        SELECT s.submission_id, s.score, s.submission_num,
               s.uin, st.name AS student_name,
               CASE WHEN COUNT(f.file_id) > 0 THEN '✅' ELSE '🚫' END AS is_downloaded
        FROM submissions s
        JOIN students st ON s.uin = st.uin
        LEFT JOIN files f ON s.submission_id = f.submission_id
        WHERE s.uin = ?
        GROUP BY s.submission_id
        ORDER BY s.submission_num
    """, (uin,))

    rows = curs.fetchall()
    columns = [desc[0] for desc in curs.description]

    curs.close()
    conn.close()

    return columns, rows


def get_undownloaded_submission_ids_by_uin(assn_name: str, uin: int):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    curs.execute("""
        SELECT s.submission_id
        FROM submissions s
        LEFT JOIN files f ON s.submission_id = f.submission_id
        WHERE s.uin = ? AND f.file_id IS NULL
    """, (uin,))

    ids = [row[0] for row in curs.fetchall()]

    curs.close()
    conn.close()

    return ids


def insert_downloaded_files(assn_name: str, submission_id: int, files_dict: dict):
    db_path = Path(".") / "configs" / assn_name / f"{assn_name}.db"
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()

    file_rows = [(submission_id, fname, ftext) for fname, ftext in files_dict.items()]
    curs.executemany(
        "INSERT INTO files (submission_id, file_name, file_text) VALUES (?, ?, ?)",
        file_rows
    )

    conn.commit()
    curs.close()
    conn.close()
