# mcps-ai

CLI para instalar y actualizar los [MCPs-AI](https://github.com/CRISTOP-bot/mcps-ai) — 8 servidores MCP universales para Claude, OpenCode, Kiro, Cursor, Windsurf, OpenClaw y más.

## Instalación

```bash
npx mcps-ai install
```

O instalar globalmente:

```bash
npm install -g mcps-ai
mcps-ai install
```

## Qué hace `install`

1. **Detecta automáticamente** tus agentes de IA instalados: OpenCode, Claude Desktop, Claude Code, Cursor, Kiro, Windsurf, OpenClaw
2. **Clona el repo** de MCPs en `~/.mcps-ai/repo`
3. **Instala dependencias Python** (uv + requirements)
4. **Pregunta solo tus credenciales** (token de Telegram, RCON de Minecraft)
5. **Escribe la config** de cada agente detectado
6. **Crea backups** `.bak` antes de tocar cualquier config existente

## Comandos

```bash
mcps-ai install        # Detecta e instala todo
mcps-ai install opencode claude  # Solo agentes específicos
mcps-ai update         # Actualiza sin perder tus .env
mcps-ai status         # Muestra agentes detectados
mcps-ai doctor         # Diagnóstico
```

## Actualizaciones seguras

`mcps-ai update` hace `git pull` del repo y reinstala dependencias, **conservando tus `.env` y credenciales**. Nunca sobrescribe tu `TELEGRAM_BOT_TOKEN` si no lo pones explícitamente.

## MCPs incluidos

- **Telegram** — Agente remoto OpenCode-Telegram (bot + worker)
- **WhatsApp** — Bridge Go + escribe mensajes
- **Minecraft** — 21 herramientas RCON
- **Gmail** — 19 herramientas OAuth2
- **Filesystem** — 14 herramientas (leer/escribir/buscar)
- **System** — 18 herramientas (CPU/RAM/procesos)
- **Web** — 4 herramientas (búsqueda Bing)
- **Browser** — 17 herramientas Playwright

## Requisitos

- Node.js 16+
- Python 3.10+
- uv
