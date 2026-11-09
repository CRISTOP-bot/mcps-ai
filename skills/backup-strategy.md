---
name: backup-strategy
description: Estrategia de backup — qué, dónde, cuánto tiempo, verificación. Se activa cuando se diseña un plan de respaldo.
---

# Skill: Backup

## Regla 3-2-1
3 copias, 2 tipos de medio, 1 offsite

## Para mcps-ai
- `mcps-ai backup` → credenciales en Gist privado
- `*.db` importantes: copias periódicas
- Verificar RESTAURACIÓN al menos una vez

## Automatizar
systemd timer o cron + prueba de restore mensual
