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
    cookies = {
        "remember_me": remember_me,
        "signed_token": signed_token,
    }

    url = f"https://www.gradescope.com/courses/{course_id}/assignments/{assn_id}/submissions/{submission_id}.zip"

    # Download the submission zip
    response = requests.get(url, cookies=cookies)
    response.raise_for_status()

    # Put all files into a files_dict, mapping file name -> file content
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        files_dict = {
            name: z.read(name).decode("utf-8")
            for name in z.namelist()
            if not name.endswith("/") and name != "metadata.yml"
        }
    
    return files_dict
