---
name: performance-tuning
description: Optimizar performance del agente y MCPs — memoria, timeout, concurrencia. Se activa cuando hay lentitud.
---

# Skill: Performance tuning

## Worker Telegram
- `REQUEST_TIMEOUT=0` → tareas pueden correr indefinidamente
- `max_concurrent=3` en TaskManager
- Polling cada 3s para progreso

## MCPs
- Evitar `sleep` largos en handlers de tools
- Timeouts en requests HTTP (10s)
- No retener clientes opencode cerrados (`close()`)

## Memoria
- `journalctl --user --disk-usage` → logs ocupando GB?
- `find . -name "*.log" -size +100M` → logs gigantes

## Si el agente va lento
1. `sys_processes("python")` → ¿hay procesos zombie?
2. `sys_memory()` → ¿RAM saturada?
3. `sys_top(10)` → ¿CPU al 100%?
