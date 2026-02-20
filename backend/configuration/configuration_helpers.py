import yaml
import sqlite3
import os
import shutil
from pathlib import Path
import platform
from datetime import datetime, timedelta
import json


# Clears out database stuff if canceled
def clear_config_dir(assn_name: str):
    db_folder_path = Path("..") / "configs" / assn_name

    if os.path.exists(db_folder_path) and os.path.isdir(db_folder_path):
        try:
            shutil.rmtree(db_folder_path)
            print(f"Folder '{db_folder_path}' has been deleted successfully.")
        except PermissionError:
            print(f"Permission denied to delete the folder '{db_folder_path}'.")
        except OSError as e:
            print(f"Error occurred while deleting the folder: {e}")


def make_config_json(
    assn_name: str,
    assn_path: Path,
    due_date: datetime,
    has_late_due_date: bool,
    late_due_date: datetime=None,
    has_network_settings: str="No",
    course_id: int=None,
    assignment_id: int=None,
    remember_me_cookie: str=None,
    signed_token_cookie: str=None
):
    config_dict = {}
    config_dict["assignment_name"] = assn_name
    config_dict["assignment_path"] = str(assn_path)
    config_dict["due_date"] = due_date.strftime("%Y-%m-%d %H:%M:%S")
    config_dict["has_late_due_date"] = has_late_due_date
    if (has_late_due_date and late_due_date != None):
        config_dict["late_due_date"] = late_due_date.strftime("%Y-%m-%d %H:%M:%S")
    config_dict["has_network_settings"] = has_network_settings
    if has_network_settings == "Yes":
        config_dict["course_id"] = course_id
        config_dict["assignment_id"] = assignment_id
        config_dict["remember_me_cookie"] = remember_me_cookie
        config_dict["signed_token_cookie"] = signed_token_cookie

    db_folder_path = Path(".") / "configs" / assn_name
    with open(os.path.join(db_folder_path, f"{assn_name}.config.json"), "w") as fjson:
        json.dump(config_dict, fjson, indent=4)
