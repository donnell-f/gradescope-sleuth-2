import yaml
import sqlite3
import os
import platform
from datetime import datetime, timedelta
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

ymlloader = yaml.CSafeLoader

# # #
# # #  Useless for revised database, but helpful for reference
# # #
def make_submission_history(submission_dict: dict, final_sub_id: int):
    submission_path = [
        (
            h[":created_at"],
            float(h[":score"]),
            int(h[":id"])
        ) 
        for h in submission_dict[":history"]
    ]
    submission_path.append( (submission_dict[":created_at"], submission_dict[":score"], final_sub_id) )

    submission_history = []
    for spi in range(len(submission_path)):
        if (spi != 0):
            submission_history.append(
                {
                    'created_at': submission_path[spi][0].strftime("%Y-%m-%d %H:%M:%S"),
                    'time_delta': (submission_path[spi][0] - submission_path[spi - 1][0]).total_seconds(),
                    'score': round(submission_path[spi][1], 2),
                    'submission_id': submission_path[spi][2]
                }
            )
        else:
            submission_history.append(
                {
                    'created_at': submission_path[spi][0].strftime("%Y-%m-%d %H:%M:%S"),
                    'time_delta': 0.0,
                    'score': round(submission_path[spi][1], 2),
                    'submission_id': submission_path[spi][2]
                }
            )

    return json.dumps(submission_history)


def initialize_database():
    #######get console input (useless)##############
    assignment_name = input("What would you like to call this assignment?: ")
    assignment_name = assignment_name.strip()

    # Letting the user retry this one bc I could see this being a bit tricky.
    # Get on-time due date
    due_date = None
    while (due_date == None):
        due_date_input = input("When is the assignment due? Enter due date in 24-hour time (YYYY-MM-DD HH:MM): ")
        due_date_input = due_date_input.strip() + ":59"     # Add the last few seconds for completeness
        try:
            due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M:%S")
        except:
            print("Bad date input. Try again.")
    
    # Get late due date
    late_due_date = None
    while (late_due_date == None):
        print("What is the late due date for the assignment?")
        print("- If late submissions are not allowed, leave this blank.")
        print("- If late submissions are allowed, enter date in one of these formats:")
        print("    - \"+<days> days\", meaning <days> days after the deadline.")
        print("    - \"YYYY-MM-DD HH:MM\", meaning 24-hour timestamp.")
        late_date_input = input("Late due date: ")
        late_date_input = late_date_input.strip()

        # If no late due date
        if (late_date_input == ""):
            late_due_date = due_date
            break

        # If days delta
        elif (late_date_input[0] == "+"):
            days_delta = int(late_date_input.split(' ')[0][1:])
            late_due_date = due_date + timedelta(days=days_delta)
            break

        # If 24-hour timestamp
        else:
            late_date_input = late_date_input + ":59"     # Add the last few seconds for completeness
            try:
                late_due_date = datetime.strptime(late_date_input, "%Y-%m-%d %H:%M:%S")
            except:
                print("Bad date input. Try again.")
    
    ################################################

    # Begin the initialization process by loading submission_metadata.yml
    submissions = None
    print("Loading submission_metadata.yml, this could take a while...")
    with open("../submission_metadata.yml", "r") as f:
        submissions = yaml.load(f, Loader=ymlloader)
    if (submissions == None):
        print("ERROR: failed to load submission_metadata.yml. Shutting down.")
        exit()

    # Return a list of detected deliverable file names, use it to generate column headers
    deliverable_fnames = detect_deliverables(submissions)
    deliverable_colnames = [d.lower().replace(".", "_") for d in deliverable_fnames]
    deliverable_cols = [d + " TEXT" for d in deliverable_colnames]

    table_colnames = ["submission_id"] + deliverable_colnames + ["student_name", "uin", "email", "first_timestamp", "last_timestamp", "final_score", "attempt_count", "submission_history"]
    table_columns = ["submission_id INTEGER PRIMARY KEY"] + deliverable_cols + ["student_name TEXT NOT NULL", "uin INTEGER NOT NULL", "email TEXT", "first_timestamp TEXT", "last_timestamp TEXT", "final_score REAL", "attempt_count INTEGER", "submission_history TEXT"]

    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    # Create the submissions table
    curs.execute('''DROP TABLE IF EXISTS submissions''')     # Drop old version, if it exists
    curs.execute(f"CREATE TABLE IF NOT EXISTS submissions ({", ".join(table_columns)})")

    # Dictionary with empty string as placeholder
    deliverables_dict = {cname: "" for cname in deliverable_colnames}
    # Add all submission metadata to database
    total_submissions_count = 0
    for s in submissions:
        print(f"Uploading {total_submissions_count+1}/{len(submissions)} submssions to database. Current submission: {s}.")
        submission_id = int(s[s.index('_')+1:])

        # Try reading all deliverables, if they exist
        # If they don't exist, they will just default to empty string
        for j in range(len(deliverable_fnames)):
            try:
                if (os.path.isfile(f"../{s}/{deliverable_fnames[j]}")):
                    with open(f"../{s}/{deliverable_fnames[j]}", "r") as f:
                        deliverables_dict[deliverable_colnames[j]] = f.read()
                else:
                    print(f">>> Submission {submission_id} does not have the file {deliverable_fnames[j]}. Skipping...")
            except:
                print(f">>> Could not read file ../{s}/{deliverable_fnames[j]}. Skipping...")

        # Add stuff to db
        last_timestamp = submissions[s][":created_at"].strftime("%Y-%m-%d %H:%M:%S")    # yml autoconverts to datetime, so strftime is needed
        first_timestamp = None
        attempt_count = len(submissions[s][":history"]) + 1    # Last attempt is not included in :history
        if (attempt_count > 1):
            first_timestamp = submissions[s][":history"][0][":created_at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            first_timestamp = last_timestamp
        submission_history = make_submission_history(submissions[s], int(s[s.index('_') + 1: ]))

        inserted_values = (submission_id,) + \
                        tuple(deliverables_dict[cn] for cn in deliverable_colnames) + \
                        (submissions[s][":submitters"][0][":name"],
                         submissions[s][":submitters"][0][":sid"],
                         submissions[s][":submitters"][0][":email"],
                         first_timestamp,
                         last_timestamp,
                         submissions[s][":score"],
                         attempt_count,
                         submission_history)
        question_marks = ",".join(['?' for _ in range(len(inserted_values))])
        curs.execute(f'''INSERT INTO submissions({", ".join(table_colnames)}) VALUES ({question_marks})''', inserted_values)

        total_submissions_count += 1


    # Write relevant config info to config.json
    try:
        config_dict = {}
        config_dict["assignment_name"] = assignment_name
        config_dict["due_date"] = due_date.strftime("%Y-%m-%d %H:%M:%S")
        config_dict["late_due_date"] = late_due_date.strftime("%Y-%m-%d %H:%M:%S")
        config_dict["deliverables_column_file_mapping"] = {deliverable_colnames[i]: deliverable_fnames[i] for i in range(len(deliverable_colnames))}
        config_dict["submissions_count_total"] = total_submissions_count     # Not necessary, but perhaps good to know
        with open("config.json", "w") as fjson:
            json.dump(config_dict, fjson, indent=4)
    except:
        print("ERROR: could not write config info to config.json. Shutting down.")
        exit()

    # Commit changes and close
    conn.commit()
    curs.close()
    conn.close()
    




def initialize_all():
    # Change into gradescope-sleuth folder since we will be running this as a module
    os.chdir("./gradescope-sleuth")

    # Print the logo
    with open("./logo.txt", "r") as f:
        print(f.read())

    # Test for config.json. If it doesn't exist, then the project hasn't been initialized, so initialize it.    
    submissions = None
    if (not os.path.isfile("./config.json")):
        init_input = input("No config.json file detected. Want to initialize the program? (y/n): ")
        if (init_input.lower() != "y"):
            print("Alright. See you later.")
            exit()
        print("Initializing program...")
        initialize_database()
        print("Initialization complete!")
    
    # Load data from config.json
    config_dict = None
    try:
        with open("config.json", "r") as fjson:
            config_dict = json.load(fjson)
    except:
        print("ERROR: could not load config.json! Shutting down...")
        exit()
    assn_name = config_dict['assignment_name']

    # Create command history file if not exists
    if (not os.path.isfile("./command_history.log")):
        with open("./command_history.log", "a") as histf:
            pass
    
    # Create the prompt session
    prompt_session = PromptSession(history=FileHistory("command_history.log"))

    return {
        "config_dict": config_dict,
        "assn_name": assn_name,
        "prompt_session": prompt_session
    }

