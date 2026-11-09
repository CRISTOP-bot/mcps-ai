"""SQLite persistence for Orchestrator MCP: agents, blackboard, messages, runs."""
import json
import sqlite3
import time
import uuid
from pathlib import Path

from config import DATABASE_PATH

Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

_conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
_conn.execute("PRAGMA journal_mode=WAL")

_conn.executescript("""
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    session_id TEXT NOT NULL,
    model_id TEXT DEFAULT '',
    system_prompt TEXT DEFAULT '',
    created_at REAL NOT NULL,
    last_active REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS blackboard (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    workers_json TEXT DEFAULT '{}',
    result TEXT DEFAULT '',
    created_at REAL NOT NULL,
    finished_at REAL
);
""")
_conn.commit()


def add_agent(name, role, session_id, model_id="", system_prompt=""):
    agent_id = uuid.uuid4().hex[:12]
    now = time.time()
    _conn.execute(
        "INSERT INTO agents (id, name, role, session_id, model_id, system_prompt, created_at, last_active) VALUES (?,?,?,?,?,?,?,?)",
        (agent_id, name, role, session_id, model_id, system_prompt, now, now),
    )
    _conn.commit()
    return agent_id


def list_agents():
    rows = _conn.execute(
        "SELECT id, name, role, session_id, model_id, created_at, last_active FROM agents ORDER BY created_at DESC"
    ).fetchall()
    keys = ("id", "name", "role", "session_id", "model_id", "created_at", "last_active")
    return [dict(zip(keys, row)) for row in rows]


def get_agent(agent_id):
    row = _conn.execute(
        "SELECT id, name, role, session_id, model_id, system_prompt FROM agents WHERE id = ?", (agent_id,)
    ).fetchone()
    if not row:
        return None
    keys = ("id", "name", "role", "session_id", "model_id", "system_prompt")
    return dict(zip(keys, row))


def touch_agent(agent_id):
    _conn.execute("UPDATE agents SET last_active = ? WHERE id = ?", (time.time(), agent_id))
    _conn.commit()


def delete_agent(agent_id):
    _conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    _conn.commit()


def blackboard_write(key, value):
    now = time.time()
    _conn.execute(
        "INSERT INTO blackboard (key, value, updated_at) VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (key, value, now),
    )
    _conn.commit()
    return now


def blackboard_read(key):
    row = _conn.execute("SELECT value, updated_at FROM blackboard WHERE key = ?", (key,)).fetchone()
    if not row:
        return None
    return {"key": key, "value": row[0], "updated_at": row[1]}


def blackboard_list():
    rows = _conn.execute("SELECT key, updated_at FROM blackboard ORDER BY updated_at DESC").fetchall()
    return [{"key": r[0], "updated_at": r[1]} for r in rows]


def blackboard_delete(key):
    _conn.execute("DELETE FROM blackboard WHERE key = ?", (key,))
    _conn.commit()


def log_message(run_id, agent_name, role, content):
    _conn.execute(
        "INSERT INTO messages (run_id, agent_name, role, content, ts) VALUES (?,?,?,?,?)",
        (run_id, agent_name, role, content, time.time()),
    )
    _conn.commit()


def get_messages(limit=20, run_id=""):
    if run_id:
        rows = _conn.execute(
            "SELECT run_id, agent_name, role, content, ts FROM messages WHERE run_id = ? ORDER BY id DESC LIMIT ?",
            (run_id, limit),
        ).fetchall()
    else:
        rows = _conn.execute(
            "SELECT run_id, agent_name, role, content, ts FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    keys = ("run_id", "agent_name", "role", "content", "ts")
    return [dict(zip(keys, row)) for row in rows]


def create_run(goal):
    run_id = uuid.uuid4().hex[:12]
    _conn.execute(
        "INSERT INTO runs (id, goal, status, created_at) VALUES (?,?,?,?)",
        (run_id, goal, "running", time.time()),
    )
    _conn.commit()
    return run_id


def finish_run(run_id, workers, status, result):
    _conn.execute(
        "UPDATE runs SET status = ?, workers_json = ?, result = ?, finished_at = ? WHERE id = ?",
        (status, json.dumps(workers, ensure_ascii=False), result, time.time(), run_id),
    )
    _conn.commit()


def list_runs(limit=10):
    rows = _conn.execute(
        "SELECT id, goal, status, created_at, finished_at FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    keys = ("id", "goal", "status", "created_at", "finished_at")
    return [dict(zip(keys, row)) for row in rows]


def stats():
    return {
        "agents": _conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0],
        "runs": _conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
        "blackboard_entries": _conn.execute("SELECT COUNT(*) FROM blackboard").fetchone()[0],
        "messages": _conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
    }
