---
name: database-sqlite
description: Trabajar con SQLite en los MCPs — esquema, queries, migrations. Se activa cuando se modifica la DB.
---

# Skill: SQLite

## Schema del worker
```sql
CREATE TABLE sessions (
  chat_id INTEGER PRIMARY KEY,
  opencode_session_id TEXT NOT NULL,
  created_at REAL, updated_at REAL
);
CREATE TABLE task_state (
  update_id INTEGER PRIMARY KEY,
  chat_id INTEGER, status TEXT,
  created_at REAL, completed_at REAL, result TEXT
);
CREATE TABLE worker_state (key TEXT PRIMARY KEY, value TEXT);
```

## Queries
```python
conn.execute("SELECT * FROM sessions WHERE chat_id = ?", (chat_id,))
conn.execute("INSERT OR REPLACE INTO sessions (...) VALUES (?,?,?,?,?)", (...))
```

## Migration
- `ALTER TABLE sessions RENAME COLUMN old TO new`
- Detectar schema con PRAGMA table_info

## Reglas
- Parametrizar queries (nunca f-strings con user input)
- Transacciones para multi-statement
- `PRAGMA journal_mode=WAL`
