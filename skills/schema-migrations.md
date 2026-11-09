---
name: schema-migrations
description: Migraciones de esquema SQLite/DB seguras. Se activa cuando se modifica una tabla existente.
---

# Skill: Migraciones

## Reglas
1. Backup antes (cp db db.bak)
2. Detectar columnas con PRAGMA table_info
3. ADD COLUMN es seguro; RENAME puede romper código viejo
4. TRANSACTIONS para multi-step
5. Probar en copia antes de producción
