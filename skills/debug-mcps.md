---
name: debug-mcps
description: Depurar servidores MCP (variables, logs, JSON-RPC). Se activa cuando un MCP crashea o devuelve respuestas raras.
---

# Skill: Depurar MCPs

## Verificar que el MCP arranca
```bash
cd mcps/<nombre>-mcp && uv run python main.py < /dev/null 2>&1 | head -15
```
Problemas comunes: missing import, .env faltante, token inválido.

## Ver logs del worker Telegram
```bash
journalctl --user -u opencode-telegram-worker -f
```

## Probar MCP con JSON-RPC crudo
```bash
(echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'; sleep 3) \
  | uv run python main.py
```

## Revisar tools disponibles
```bash
(echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'; sleep 2) | uv run python main.py
```

## Errores comunes
| Síntoma | Causa | Fix |
|---------|-------|-----|
| MCP no arranca | missing .env | cp .env.example .env |
| tools/list vacío | FastMCP viejo | uv sync |
| 403 en Gmail | token expirado | python gmail_auth.py |
| Browser no abre | falta chromium | playwright install chromium |
