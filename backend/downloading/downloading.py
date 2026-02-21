import os
import requests
import zipfile
import io

def download_submission_as_dict(
    course_id: int,
    assn_id: int,
    submission_id: int,
    remember_me: str,
    signed_token: str
) -> dict[str, str]:

    # Copied from configure_new_database.py!
    valid_extensions = {
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

    cookies = {
        "remember_me": remember_me,
        "signed_token": signed_token,
    }

    url = f"https://www.gradescope.com/courses/{course_id}/assignments/{assn_id}/submissions/{submission_id}.zip"

    # Download the submission zip
    response = requests.get(url, cookies=cookies)
    response.raise_for_status()

    # Put all text files into a files_dict, mapping file name -> file content.
    # Binary files that can't be decoded as UTF-8 are skipped.
    files_dict = {}
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for name in z.namelist():
            # Don't include metadata.yml
            if name.endswith("/") or name == "metadata.yml":
                continue
            # Don't include non-code files
            if os.path.splitext(name)[1].lower() not in valid_extensions:
                continue
            try:
                # Don't include binary files
                files_dict[name] = z.read(name).decode("utf-8")
            except UnicodeDecodeError:
                pass
    
    return files_dict
