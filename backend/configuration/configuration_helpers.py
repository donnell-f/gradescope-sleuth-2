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

