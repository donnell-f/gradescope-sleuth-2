PRAGMA foreign_keys = ON;

CREATE TABLE students (
    uin INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY,
    created_at TEXT,
    score REAL,
    submission_num INTEGER,
    uin INTEGER REFERENCES students(uin)
);

CREATE TABLE files (
    file_id INTEGER PRIMARY KEY,
    submission_id INTEGER REFERENCES submissions(submission_id),
    file_name TEXT,
    file_text TEXT
);
