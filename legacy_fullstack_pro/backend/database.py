import sqlite3, json
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()

SCHEMA = '''
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 email TEXT NOT NULL UNIQUE,
 phone TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 phone_verified INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS otps(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 phone TEXT NOT NULL,
 code_hash TEXT NOT NULL,
 expires_at INTEGER NOT NULL,
 attempts INTEGER NOT NULL DEFAULT 0,
 consumed INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL,
 token_hash TEXT NOT NULL UNIQUE,
 expires_at INTEGER NOT NULL,
 created_at TEXT NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS projects(
 id TEXT PRIMARY KEY,
 user_id INTEGER NOT NULL,
 name TEXT NOT NULL,
 root_path TEXT NOT NULL,
 source_filename TEXT,
 created_at TEXT NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS analyses(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 project_id TEXT NOT NULL,
 kind TEXT NOT NULL,
 result_json TEXT NOT NULL,
 created_at TEXT NOT NULL,
 FOREIGN KEY(project_id) REFERENCES projects(id)
);
CREATE TABLE IF NOT EXISTS audit_log(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER,
 project_id TEXT,
 event TEXT NOT NULL,
 metadata_json TEXT NOT NULL,
 created_at TEXT NOT NULL
);
'''

def connect(path):
    conn=sqlite3.connect(path, timeout=20)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def init_db(path):
    with connect(path) as c: c.executescript(SCHEMA)

def audit(path, event, user_id=None, project_id=None, metadata=None):
    with connect(path) as c:
        c.execute('INSERT INTO audit_log(user_id,project_id,event,metadata_json,created_at) VALUES(?,?,?,?,?)',
                  (user_id,project_id,event,json.dumps(metadata or {}, ensure_ascii=False),now()))
