# MCPs for AI Agents

[![CI](https://github.com/CRISTOP-bot/mcps-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/CRISTOP-bot/mcps-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![npm](https://img.shields.io/npm/v/mcps-ai)](https://www.npmjs.com/package/mcps-ai)

**15 MCP servers, 230+ tools, one install command.** Works with Claude Desktop, Claude Code, Cursor, Kiro, Windsurf, OpenCode, and OpenClaw.

🌐 **Website:** https://cristop-bot.github.io/mcps-ai/ · 📖 **Wiki:** https://github.com/CRISTOP-bot/mcps-ai/wiki

## What you get

| MCP | Tools | What it does |
|-----|-------|-------------|
| **Telegram** | 32 | Agente remoto OpenCode/AI controlable por Telegram. Worker 24/7, texto plano (sin markdown), auto-cambio de modelo, progreso en tiempo real |
| **WhatsApp** | 12 | Envío/recepción de mensajes vía bridge Go (whatsmeow) |
| **Minecraft** | 21 | Control de servidor Minecraft vía RCON (dar items, teletransportar, clima, etc.) |
| **Gmail** | 19 | Leer, enviar, buscar, etiquetar, archivar emails (OAuth2) |
| **Filesystem** | 14 | Leer, escribir, buscar y gestionar archivos con seguridad (solo dirs permitidos) |
| **System** | 18 | CPU, RAM, disco, procesos, red, logs, batería, temperatura |
| **Web** | 4 | Búsqueda en la web (Bing), fetch de páginas, noticias, clima |
| **Browser** | 17 | Control interactivo de browser vía Playwright |
| **GitHub** | 16 | Repos, issues, PRs, búsqueda, releases y gists (token o `gh auth token`) |
| **Discord** | 11 | Mensajes, DMs, reacciones, canales y miembros (bot token o webhook) |
| **Spotify** | 14 | Búsqueda, play/pause, volumen, colas, playlists, dispositivos (OAuth + refresh token) |
| **Slack** | 11 | Mensajes, DMs, canales, historial, usuarios, reacciones, pins (bot token) |
| **Notion** | 11 | Búsqueda, páginas, bases de datos, bloques, usuarios (internal integration) |
| **Home Assistant** | 11 | Estados, servicios, dominios, historial y eventos del hogar (long-lived token) |
| **Orchestrator** | 12 | Coordinador multi-agente: Director + workers en paralelo, blackboard compartida, transcript |

## Install

```bash
npx mcps-ai install
```

The installer:
1. Detects your installed AI agents automatically
2. Clones this repo to `~/.mcps-ai/repo/`
3. Installs Python dependencies with `uv`
4. **Auto-configures what's trivial:** GitHub token from `gh` CLI, Playwright chromium, Orchestrator (reuses your OpenCode `AI_*` if you already have Telegram configured, detects the server port), Home Assistant (detects a local instance) — never overwrites existing `.env`
5. Prompts you only for what needs a human (Telegram token, Minecraft RCON password, API keys)
6. Writes agent configs; **creates `.bak` backups** and **preserves existing working configs**

## Tests

```bash
npm test                           # CLI internals (merge, paths, config guards)
cd mcps/filesystem-mcp && uv run python -m pytest tests/   # 28 path-security tests
cd mcps/orchestrator-mcp && uv run python -m pytest tests/ # store + role parsing
```

CI runs all of these plus import checks for all 15 MCPs and the Telegram/Minecraft suites (GitHub Actions).

## Usage

```bash
mcps-ai install [agents...]   # Install for specific agents
mcps-ai login                 # Authenticate with GitHub (gh CLI)
mcps-ai backup                # Backup credentials to private Gist
mcps-ai restore               # Restore credentials on another machine
mcps-ai status                # Show detected agents
mcps-ai doctor                # Diagnose installation
mcps-ai update                # Update (keeps your .env files)
```

## Structure

```
mcps-ai/
├── mcps/                    # Canonical MCP servers (single source of truth)
│   ├── telegram-mcp/
│   ├── whatsapp-mcp/
│   ├── minecraft-mcp/
│   ├── gmail-mcp/
│   ├── filesystem-mcp/
│   ├── system-mcp/
│   ├── web-mcp/
│   └── browser-mcp/
├── agents/                  # Per-agent config instructions
│   ├── claude/
│   ├── claude-code/
│   ├── cursor/
│   ├── kiro/
│   ├── opencode/
│   ├── openclaw/
│   └── windsurf/
├── cli/                     # mcps-ai CLI (published to npm)
├── skills/                  # 112 SKILL.md para agentes AI (instalación, uso, debugging, etc.)
├── install.md               # Detailed setup for AI agents
└── package.json
```

## Requirements

- **Node.js** 16+
- **Python** 3.10+
- **uv** (installer will install it if missing)
- **Git**

## Platforms

- **Linux** — full support (systemd services)
- **macOS** — full support (launchd plists included)
- **Windows** — partial (Linux-specific commands differ)

## Security

- Credentials live only in local `.env` files (gitignored)
- No tokens committed to the repo
- `mcps-ai backup` uses **private Gists** only
- `.bak` files are created before any config is modified

## License

MIT
