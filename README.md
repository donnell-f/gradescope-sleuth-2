# Gradescope Sleuth 2

Gradescope Sleuth 2 is a tool that allows you to easily sleuth through all submissions for a Gradescope programming assignment. It is equipped with a powerful regex engine that can catch plagiarists at mach speed.

## Getting Started

You will need to have Anaconda installed in order to run Gradescope Sleuth.

- Consider Miniconda if you are tight on disk space...

First, create and activate the conda environment.

- `conda create -f environment.yml`
- `conda activate grade_sleuth`

Then, run Gradescope Sleuth using Streamlit

- `streamlit run app.py`

Then, configure Gradescope Sleuth by giving it the absolute path to a folder of downloaded submissions.

## Features

- Regex search all submissions
    - Print list of submissions matching pattern
    - Print the matches themselves (and two lines of surrounding context)
- Print student's entire submission history at once
    - Surprisingly hard to do on Gradescope itself
- Store and reload configurations for past assignments
- [COMING SOON] Can download historical submissions in background for extra data
- [COMING SOON] Print list of students whose first submission was right before the deadline

## Support / Compatibility

Supports any Gradescope programming assignment. Completely cross platform.
