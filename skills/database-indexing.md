---
name: database-indexing
description: Índices de base de datos — cuándo crearlos, cómo medir. Se activa cuando una query es lenta.
---

# Skill: Índices DB

## Cuándo
- Columnas en WHERE/JOIN/ORDER BY frecuentes
- Queries lentas con SELECT repetido

## En SQLite
```sql
CREATE INDEX idx_chat ON messages(chat_jid, timestamp);
EXPLAIN QUERY PLAN SELECT ...;
```

## No abusar
Cada índice ralentiza writes; medir con y sin
