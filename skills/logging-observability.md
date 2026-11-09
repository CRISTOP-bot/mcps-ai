---
name: logging-observability
description: Logs y observabilidad — qué loguear, cómo ver logs, alertas. Se activa para debugging o monitoreo.
---

# Skill: Logging & observability

## Qué loguear
- Inicio/fin de requests
- Errores con traceback
- Métricas básicas (count, latency)
- NO loguear secrets

## Logs del worker
```bash
journalctl --user -u opencode-telegram-worker -f
journalctl --user -u opencode-telegram-worker --since "1 hour ago"
```

## Métricas útiles
- Requests por minuto
- Latencia promedio
- Tasa de error
- Tokens consumidos por modelo

## Si algo va mal
1. `journalctl --user --since "5 minutes ago"`
2. Buscar ERROR/WARNING
3. Revisar última task fallida en DB
