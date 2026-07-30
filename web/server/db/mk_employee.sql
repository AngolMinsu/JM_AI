CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    join_date DATE NOT NULL,
    role TEXT NOT NULL,
    certifications TEXT
);