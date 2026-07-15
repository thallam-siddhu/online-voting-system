import sqlite3

conn = sqlite3.connect("voting.db")
cursor = conn.cursor()

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    voted INTEGER DEFAULT 0
)
""")

# Votes Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS votes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    candidate TEXT,
    vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Candidates Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_name TEXT UNIQUE
)
""")

# Insert Default Candidates
cursor.execute("INSERT OR IGNORE INTO candidates(candidate_name) VALUES('Candidate A')")
cursor.execute("INSERT OR IGNORE INTO candidates(candidate_name) VALUES('Candidate B')")
cursor.execute("INSERT OR IGNORE INTO candidates(candidate_name) VALUES('Candidate C')")

conn.commit()
conn.close()

print("===================================")
print(" Online Voting Database Created ")
print("===================================")
print("Users Table      : Created")
print("Votes Table      : Created")
print("Candidates Table : Created")
print("Default Candidates Added")
print("Database Ready Successfully!")