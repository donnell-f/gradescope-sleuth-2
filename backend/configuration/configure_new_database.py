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
    db_folder_path = Path(".") / "configs" / assn_name
    os.makedirs(db_folder_path, exist_ok=True)
    conn = sqlite3.connect(os.path.join(db_folder_path, f"{assn_name}.db"))
    curs = conn.cursor()

    # Initialize the database using the db_schema.sql script
    new_db_script = None
    new_db_script_path = Path(".") / "db_schema.sql"
    with open(new_db_script_path, "r") as f_sql:
        new_db_script = f_sql.read()
    curs.executescript(new_db_script)

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

    is_valid_file = lambda f: os.path.isfile(os.path.join(folder_path, f)) \
        and os.path.splitext(f)[1].lower() in extensions \
        and f != "metadata.yml"
    return [ f for f in os.listdir(folder_path) if is_valid_file(f) ]



def make_config_json(assn_name: str, assn_path: Path, due_date: datetime, has_late_due_date: bool, late_due_date: datetime=None):
    config_dict = {}
    config_dict["assignment_name"] = assn_name
    config_dict["assignment_path"] = str(assn_path)
    config_dict["due_date"] = due_date.strftime("%Y-%m-%d %H:%M:%S")
    config_dict["has_late_due_date"] = has_late_due_date
    if (has_late_due_date and late_due_date != None):
        config_dict["late_due_date"] = late_due_date.strftime("%Y-%m-%d %H:%M:%S")

    db_folder_path = Path(".") / "configs" / assn_name
    with open(os.path.join(db_folder_path, f"{assn_name}.config.json"), "w") as fjson:
        json.dump(config_dict, fjson, indent=4)



def configure_new_database(cancel_event, assn_name: str, assn_path: Path, due_date: datetime, has_late_due_date: bool, late_due_date: datetime=None):
    # Initialize the database
    conn, curs = initialize_db(assn_name)

    # Load submission_metadata.yml
    submissions = None
    print("Loading submission_metadata.yml, this could take a while...")
    ymlloader = yaml.CSafeLoader
    with open(os.path.join(assn_path, "submission_metadata.yml"), "r") as f:
        submissions = yaml.load(f, Loader=ymlloader)
    if (submissions == None):
        print("ERROR: failed to load submission_metadata.yml. Shutting down.")
        exit()
    print("Successfully loaded submission_metadata.yml.")

    for s in submissions:
        # Periodic check for cancellation
        if cancel_event.is_set():
            curs.close()
            conn.close()
            return False
        # Get all code files uploaded for the final submission from the final
        # submission folder.
        submission_id = int(s[s.index('_')+1:])
        get_code_files_in_folder(os.path.join(assn_path, f"submission_{submission_id}"))

        # ----- Get student info ----- #
        stu_name = submissions[s][":submitters"][0][":name"]
        stu_uin = int(submissions[s][":submitters"][0][":sid"])
        stu_email = submissions[s][":submitters"][0][":email"]

        # ----- Get historical submissions data ----- #
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
        final_sub_files_data = []
        for fname in final_sub_files:
            # Read submitted file content
            f_content = ""
            try:
                with open(os.path.join(final_sub_folder, fname), "r") as f:
                    f_content = f.read()
            except Exception as e:
                print(f"Could not read deliverable file at {os.path.join(final_sub_folder, fname)}. Error: {e}")
            
            # Collect submitted file names and content into final_sub_files_content
            final_sub_files_data.append( (fname, f_content) )
        # Append submission ID to final_sub_files_data to make DB insertion easy
        final_sub_files_data = [ (submission_id, *fsfd) for fsfd in final_sub_files_data ]


        # ----- Insert collected data into database ----- #

        # Insert student
        curs.execute(
            "INSERT OR IGNORE INTO students (uin, name, email) VALUES (?, ?, ?)",
            (stu_uin, stu_name, stu_email)
        )

        # Insert historical + final submissions
        curs.executemany(
            "INSERT OR IGNORE INTO submissions (submission_id, created_at, score, submission_num, uin) VALUES (?, ?, ?, ?, ?)",
            all_submissions
        )

        # Insert final submission files
        curs.executemany(
            "INSERT INTO files (submission_id, file_name, file_text) VALUES (?, ?, ?)",
            final_sub_files_data
        )

        conn.commit()

    # Periodic check for cancellation
    if cancel_event.is_set():
        curs.close()
        conn.close()
        return False
    
    # Save the settings to a JSON file so that they can be loaded in the future
    make_config_json(assn_name=assn_name, assn_path=assn_path, due_date=due_date, has_late_due_date=has_late_due_date, late_due_date=late_due_date)

    # Wrap up db stuff
    curs.close()
    conn.close()

    # Setup (assumably) successful
    return True


