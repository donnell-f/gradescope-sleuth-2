# This file contains function that implement regex for Sqlite3. It does not come
# with a default regex engine.
# Add case sensitive regex to an Sqlite connection using the following code:
#      conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)
# Or, case insenvitive using this code:
#      conn.create_function("regexp", 2, py_regexp_cinsensitive, deterministic=True)

from datetime import datetime
import re
import functools

# Added LRU cache for speed
@functools.lru_cache(maxsize=256)
def _compile_cinsensitive(pat):
    return re.compile(pat, flags=re.IGNORECASE)
@functools.lru_cache(maxsize=256)
def _compile_csensitive(pat):
    return re.compile(pat)


# Define two implementations of the regex function: one for case insensitive, and one for case sensitive
def py_regexp_cinsensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_cinsensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0
def py_regexp_csensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_csensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0
