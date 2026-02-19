import yaml
import sqlite3
import os
import shutil
from pathlib import Path
import platform
from datetime import datetime, timedelta
import json



# Clear the config if configuration gets cancelled or something.
def clear_config():
    ## TODO
    pass

def initialize_db(assn_name: str):
    # Create the .db file and connect
    db_folder_path = Path("..") / "configs" / assn_name
    os.mkdir(db_folder_path)
    conn = sqlite3.connect(os.path.join(db_folder_path, f"{assn_name}.db"))
    curs = conn.cursor()

    # Initialize the database
    curs.execute("""
PRAGMA foreign_keys = ON;

CREATE TABLE students (
    uin INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY,
    created_at TEXT,
    score REAL,
    submission_num INTEGER,
    uin INTEGER REFERENCES students(uin)
);

CREATE TABLE files (
    file_id INTEGER PRIMARY KEY,
    submission_id INTEGER REFERENCES submissions(submission_id),
    file_text TEXT
)
    """)

    # Return the connection and cursor objects
    return (conn, curs)



def get_code_files_in_folder(folder_path: Path) -> list[str]:
    extensions = {
        # Code files
        ".cpp", ".cc", ".cxx", ".h", ".hpp",  # C++
        ".c",                                   # C
        ".js", ".mjs", ".cjs",                 # JavaScript
        ".cs",                                  # C#
        ".java",                                # Java
        ".sql",                                 # SQL
        ".sh", ".bash",                         # Bash
        ".py",                                  # Python
        ".go",                                  # Go
        # Other
        ".txt",
        ".json",
        ".html",
        ".yml", ".yaml",
    }

    return [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
        and os.path.splitext(f)[1].lower() in extensions
    ]



# Clears out database stuff if canceled
def on_config_canceled(conn, curs, assn_name: str):
    db_folder_path = Path("..") / "configs" / assn_name
    curs.close()
    conn.close()

    if os.path.exists(db_folder_path) and os.path.isdir(db_folder_path):
        try:
            shutil.rmtree(db_folder_path)
            print(f"Folder '{db_folder_path}' has been deleted successfully.")
        except PermissionError:
            print(f"Permission denied to delete the folder '{db_folder_path}'.")
        except OSError as e:
            print(f"Error occurred while deleting the folder: {e}")



def configure_database(cancel_event, assn_name: str, assn_path: Path, due_date: datetime, has_late_due_date: bool, late_due_date: datetime=None):
    # Initialize the database
    conn, curs = initialize_db(assn_name)

    # Load submission_metadata.yml
    submissions = None
    print("Loading submission_metadata.yml, this could take a while...")
    ymlloader = yaml.CSafeLoader
    with open(os.path.join(assn_path, "../submission_metadata.yml"), "r") as f:
        submissions = yaml.load(f, Loader=ymlloader)
    if (submissions == None):
        print("ERROR: failed to load submission_metadata.yml. Shutting down.")
        exit()
    print("Successfully loaded submission_metadata.yml.")

    for s in submissions:
        # Get all code files uploaded for the final submission from the final
        # submission folder.
        submission_id = int(s[s.index('_')+1:])
        get_code_files_in_folder(os.path.join(assn_path, f"submission_{submission_id}"))

        # Get student info
        stu_name = submissions[s][":submitters"][0][":name"]
        stu_uin = int(submissions[s][":submitters"][0][":sid"])
        stu_email = submissions[s][":submitters"][0][":email"]

        # ----- Gather historical submissions data ----- #
        # NOTE: yml autoconverts to datetime. That's why a strftime is needed
        # below. Sqlite3 can only store dates as strings.
        all_submissions = []
        for hist in submissions[s][":history"]:
            all_submissions.append( (hist[":id"], hist[":created_at"].strftime("%Y-%m-%d %H:%M:%S"), hist[":score"]) )
        # Append final submission
        all_submissions.append( (submission_id, submissions[s][":created_at"].strftime("%Y-%m-%d %H:%M:%S"), submissions[s][":score"]) )
        # Enumerate submissions (1-indexed)
        all_submissions = [ (*hist, i+1) for (i, hist) in enumerate(all_submissions) ]
        # Add submitter UIN to submissions
        all_submissions = [ (*hist, stu_uin) for hist in all_submissions ]
        # Remember that Gradescope only downloads each student's *last*
        # submission, so that's what you will be getting from the folders.

        # ----- Get final submission files ----- #
        final_sub_folder = os.path.join(assn_path, f"submission_{submission_id}")
        final_sub_files = get_code_files_in_folder(final_sub_folder)
        


        ### DATABASE INSERTION CODE HERE

        


# # Placeholder configure_database code for testing...
# def configure_database(cancel_event, assn_name, assn_path, due_date, has_late_due_date, late_due_date=None):
#     """Placeholder: sleeps for 2 seconds, checking for cancellation.
#     Returns True on success, False otherwise."""
#     for _ in range(20):
#         if cancel_event.is_set():
#             return False
#         time.sleep(0.1)
#     print("Done!")
#     return True




