---
name: cron-scheduling
description: Programar tareas con cron — sintaxis y debugging. Se activa cuando el usuario quiere ejecutar algo periódicamente.
---

# Skill: cron

## Sintaxis
```
# min hora día mes día-semana comando
0 9 * * *  /ruta/script.sh     # 9:00 diario
*/15 * * * *  /ruta/check.sh   # cada 15 min
0 0 * * 0  /ruta/weekly.sh     # domingos medianoche
```

## Crontab
```bash
crontab -e   # editar
crontab -l   # listar
```

## Gotchas
- Entorno mínimo: usar rutas absolutas
- Redirigir output: `>> log 2>&1`
