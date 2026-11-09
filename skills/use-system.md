---
name: use-system
description: Información del sistema — CPU, RAM, disco, procesos, red, logs, temperatura. Se activa cuando el usuario pide "qué está pasando" en la máquina.
---

# Skill: Usar System

## Herramientas disponibles (namespace `system`)
- `sys_info()` — OS, kernel, hostname, arquitectura, uptime
- `sys_processes(filter_name, limit)` — listar procesos
- `sys_top(lines)` — CPU/memoria en tiempo real
- `sys_cpu()`, `sys_memory()`, `sys_disk()` — métricas vitales
- `sys_network()`, `sys_ports()` — red e interfaces
- `sys_env_vars(filter_name)` — variables de entorno (oculta secrets)
- `sys_logs(path, lines)` — leer logs
- `sys_services()`, `sys_services_failed()` — servicios corriendo/fallidos
- `sys_who()` — usuarios logueados
- `sys_uptime()` — tiempo de actividad
- `sys_kill_process(pid, signal)` / `sys_kill_by_name(name, signal)`
- `sys_temperature()`, `sys_battery()` — temperatura y batería

## Reglas
1. No matar procesos del sistema sin confirmación.
2. No exponer secrets de env_vars en outputs.
3. Para diagnosticar, usar primero `sys_info()` y `sys_processes()` como base.
4. Si el usuario pide "qué está pasando", usar `sys_top` + `sys_cpu` + `sys_memory`.
