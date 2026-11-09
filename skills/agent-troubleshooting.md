---
name: agent-troubleshooting
description: Diagnosticar y arreglar problemas comunes de los MCPs (worker caído, conexión perdida, auth fallida). Se activa cuando algo no funciona.
---

# Skill: Diagnóstico de MCPs

## Síntomas y causas comunes

### Telegram no responde / stale responses
- Causa: worker caído o bug de conteo de mensajes
- Fix: reiniciar servicio `systemctl --user restart opencode-telegram-worker`
- Verificar logs: `journalctl --user -u opencode-telegram-worker -f`

### Browser: "Executable doesn't exist"
- Causa: falta `playwright install chromium`
- Fix: `cd mcps/browser-mcp && uv run playwright install chromium`

### Gmail: "Gmail not authenticated"
- Causa: falta `token.json`
- Fix: `python gmail_auth.py` (abre navegador)

### npm publish 403/401
- Causa: token sin bypass 2FA
- Fix: crear Granular Access Token con Publish + Bypass 2FA

### mcps-ai repo no clonado
- Fix: `mcps-ai install --source` o dejar que clone automáticamente

### Configs mezcladas tras upgrade
- Fix: `mcps-ai doctor` muestra paths; verificar `.env`

## Diagnóstico rápido
1. `mcps-ai doctor` — estado general
2. `mcps-ai status` — agentes detectados
3. Verificar procesos: `pgrep -af telegram_worker.py`
4. Logs: `journalctl --user -u opencode-telegram-worker -f`
