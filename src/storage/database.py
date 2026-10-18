from pathlib import Path
import sqlite3
from contextlib import contextmanager

SRC_DIR = Path(__file__).resolve().parent.parent
DB_PATH = SRC_DIR / "netpeer.db"

# Use context manager to handle database connections and ensure cleanup
@contextmanager
def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def init_database():
    """
    Initizalizes the database with the necessary tables for storing ping sessions and results
    """
    with _connect() as connection:
        connection.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT
                )
                ''')
        connection.execute('''
                    CREATE TABLE IF NOT EXISTS ping_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    timestamp TEXT,
                    status TEXT,
                    latency_ms INTEGER,
                    jitter_ms INTEGER,
                    is_spike INTEGER,
                    error_message TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                ''')

def insert_session(target, started_at):
    with _connect() as connection:
        cur = connection.execute('''
                INSERT INTO sessions (target, started_at)
                VALUES (?, ?)
                ''', (target, started_at))
        return cur.lastrowid

def insert_ping_result(session_id, timestamp, status, latency_ms, jitter_ms, is_spike, error_message):
    with _connect() as connection:
        connection.execute('''
                INSERT INTO ping_results (session_id, timestamp, status, latency_ms, jitter_ms, is_spike, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, timestamp, status, latency_ms, jitter_ms, is_spike, error_message))

def update_session_end_time(session_id, ended_at):
    with _connect() as connection:
        connection.execute('''
                UPDATE sessions
                SET ended_at = ?
                WHERE id = ?
                ''', (ended_at, session_id))

def get_sessions():
    with _connect() as connection:
        cur = connection.execute('''
                SELECT * FROM sessions
                ORDER BY id DESC
                ''')
        return cur.fetchall()

def get_session_results(session_id):
    with _connect() as connection:
        cur = connection.execute('''
                SELECT * FROM ping_results
                WHERE session_id = ?
                ORDER BY id ASC
                ''', (session_id,))
        return cur.fetchall()