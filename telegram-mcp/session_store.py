"""SQLite persistence for Telegram-OpenCode sessions."""

import sqlite3
import json
import time
import threading
from contextlib import contextmanager
from config import get_db_path


class SessionStore:
    """Manages persistent storage of chat sessions, tasks, and state."""

    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    chat_id INTEGER PRIMARY KEY,
                    opencode_session_id TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    directory TEXT
                );
                CREATE TABLE IF NOT EXISTS task_state (
                    update_id INTEGER PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at REAL NOT NULL,
                    completed_at REAL,
                    result TEXT
                );
                CREATE TABLE IF NOT EXISTS worker_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_task_chat ON task_state(chat_id);
                CREATE INDEX IF NOT EXISTS idx_task_status ON task_state(status);
            """)

    @contextmanager
    def _connect(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    # --- Sessions ---

    def get_session(self, chat_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE chat_id = ?", (chat_id,)
            ).fetchone()
            if row:
                return dict(row)
            return None

    def save_session(self, chat_id, session_id, directory=None):
        now = time.time()
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO sessions (chat_id, opencode_session_id, created_at, updated_at, directory)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    opencode_session_id = excluded.opencode_session_id,
                    updated_at = excluded.updated_at,
                    directory = excluded.directory
            """, (chat_id, session_id, now, now, directory))

    def delete_session(self, chat_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE chat_id = ?", (chat_id,))

    def touch_session(self, chat_id):
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE chat_id = ?",
                (time.time(), chat_id)
            )

    def list_sessions(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
            return [dict(r) for r in rows]

    # --- Task state ---

    def is_processed(self, update_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM task_state WHERE update_id = ?", (update_id,)
            ).fetchone()
            return row is not None

    def mark_processed(self, update_id, chat_id, status="completed", result=None):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO task_state (update_id, chat_id, status, created_at, completed_at, result)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(update_id) DO UPDATE SET
                    status = excluded.status,
                    completed_at = excluded.completed_at,
                    result = excluded.result
            """, (update_id, chat_id, status, time.time(), time.time(), result))

    def get_pending_tasks(self, chat_id=None):
        with self._connect() as conn:
            if chat_id:
                rows = conn.execute(
                    "SELECT * FROM task_state WHERE chat_id = ? AND status = 'pending' ORDER BY created_at",
                    (chat_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM task_state WHERE status = 'pending' ORDER BY created_at"
                ).fetchall()
            return [dict(r) for r in rows]

    # --- Worker state ---

    def get_state(self, key, default=None):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM worker_state WHERE key = ?", (key,)
            ).fetchone()
            if row:
                return row["value"]
            return default

    def set_state(self, key, value):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO worker_state (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))

    def get_last_update_id(self):
        val = self.get_state("last_update_id", "0")
        return int(val)

    def set_last_update_id(self, update_id):
        self.set_state("last_update_id", str(update_id))
