# 🫆 Gradescope Sleuth 2

Gradescope Sleuth 2 is a tool that allows you to easily sleuth through all submissions for a Gradescope programming assignment. It is equipped with a powerful regex engine that can catch plagiarists at mach speed.

## Starting Gradescope Sleuth 2

You will need to have Anaconda installed in order to run Gradescope Sleuth.

- Consider Miniconda if you are tight on disk space...

First, create and activate the conda environment.

- `conda create -f environment.yml`
- `conda activate grade_sleuth`

Then, run Gradescope Sleuth using Streamlit

- `streamlit run app.py`

Then, configure Gradescope Sleuth by giving it the absolute path to a folder of downloaded submissions.

## Configuration

I would like to clarify a few things about configuration

1. The configuration name will be used to save a new configuration to the `configs` folder.
2. The "Course ID" and "Assignment ID" number inputs may be confusing. You can find these by going to a Gradescope assignment's homepage and looking at the URL. You should be able to easily find the course and assignment IDs in there. In general, Gradescope reveals a lot of information in its URLs.
3. Loading an existing configuration should be almost instant.
4. Creating a new configuration may take a **long** time. It depends on your computer.

## Features

- Regex search all submissions
    - Print list of submissions matching pattern
    - Print the matches themselves (and two lines of surrounding context)
- Print student's entire submission history at once
    - Surprisingly hard to do on Gradescope itself
- Store and reload configurations for past assignments
- Can download historical submissions in background for extra data
- [COMING SOON] Print list of students whose first submission was right before the deadline

## Support / Compatibility

Supports any Gradescope programming assignment. Completely cross platform.

## Notes

- All regex is case sensitive, for now.
- Ask me if you would like any new features.
