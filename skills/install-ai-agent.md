---
name: install-ai-agent
description: Instalar los MCPs y configurar un agente de IA (Claude, OpenCode, Kiro, Cursor, Windsurf, OpenClaw). Se activa cuando el usuario pide instalar o configurar los MCPs en su editor/agente.
---

# Skill: Instalar AI Agent (cualquier editor)

## Flujo automático
```bash
npx mcps-ai install
```
Esto detecta tu agente y configura todo solo.

## Configuración manual
Edita el archivo de config según tu agente:
- Claude Desktop → `~/.config/claude/claude_desktop_config.json`
- Claude Code → `.mcp.json` en la raíz del proyecto
- Cursor → `.cursor/mcp.json` en la raíz del proyecto
- Kiro → `~/.kiro/settings/mcp.json`
- OpenCode → `~/.config/opencode/opencode.json`
- OpenClaw → `~/.openclaw/config.json` → `mcp.servers`
- Windsurf → `~/.codeium/windsurf/mcp_config.json`

Agrega cada servidor con `"command": "uv", "args": ["--directory", "<repo>/mcps/<nombre>", "run", "main.py"]`.

## Credenciales necesarias
- Telegram → seed_bot_token (de @BotFather)
- Minecraft → RCON password del servidor
- Gmail → OAuth: `python gmail_auth.py` (abre navegador)
- WhatsApp → bridge por QR
- Browser → `uv run playwright install chromium`

## Actualizar
```bash
mcps-ai update   # git pull → reinstala deps, preserva .env
```
