from datetime import datetime
import re
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight

from .IndexLineMapper import IndexLineMapper

# Get the in-context matches given a regex pattern and a file (and some other decorative data)
def get_in_context_matches(
    pattern: str,
    submission_id: int,
    file_name: str,
    file_text: str,
    student_name: str,
    uin: str,
    email: str,
    case_sensitive: bool
):

    # The string that will be returned
    output_string = ""

    # IndexLineMapper instance
    ilm = IndexLineMapper(file_text)

    # Format header
    matches_header = f"Submission {submission_id}  -  {student_name}, {uin}, {email}  -  {file_name}"
    line_ext_length = len(matches_header) + len(str(ilm.getMaxLineNum())) + 3


    # Save all matches with context to matches_with_context
    matches = None
    if case_sensitive:
        matches = re.finditer(pattern, file_text)
    else:
        matches = re.finditer(pattern, file_text, re.IGNORECASE)

    # Store matches with context here. Will be concatenated into one big `output_string` later.
    matches_with_context = []
    for m in matches:
        firstline = ilm.stringIndexToLineNum(m.start())
        lastline = ilm.stringIndexToLineNum(m.end() - 1)
        all_line_nums = [lnum for lnum in range(firstline, lastline + 1)]
        matches_with_context.append(ilm.getNumberedLinesWithContext(all_line_nums, context_radius=1))
    
    # Only print header if there were no matches
    if (matches_with_context == []):
        output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
        output_string += (3*' ' + matches_header) + "\n"
        output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
        return output_string
    
    # Print student info header
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
    output_string += (3*' ' + matches_header) + "\n"
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "─┬─" + line_ext_length*'─') + "\n"

    # Print the matches stored with matches_with_context
    output_string += (('\n' + len(str(ilm.getMaxLineNum()))*'─' + "─┼─" + line_ext_length*'─' + "\n").join(matches_with_context)) + "\n"
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "─┴─" + line_ext_length*'─') + "\n"

    return output_string


