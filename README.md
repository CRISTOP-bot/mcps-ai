# MCPs para IA

> Colección de servidores MCP (Model Context Protocol) universales para agentes de IA.

[![GitHub](https://img.shields.io/badge/GitHub-mcps--ai-blue?logo=github)](https://github.com/CRISTOP-bot/mcps-ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Tabla de contenidos

- [MCPs incluidos](#mcps-incluidos)
- [Compatibilidad](#compatibilidad)
- [Instalación rápida](#instalación-rápida)
- [Estructura](#estructura)
- [Seguridad](#seguridad)
- [Licencia](#licencia)

## 🧩 MCPs incluidos

### 1. Telegram Remote Agent (`mcps/telegram-mcp/`)

Convierte tu computadora en un servidor de OpenCode controlable remotamente via Telegram.

**Características:**
- Worker persistente con long polling (24/7)
- Integración con OpenCode Server API
- SQLite para persistencia de sesiones y tareas
- Auto-cambio de modelo cuando se acaban los tokens (11 modelos de respaldo)
- Sin timeout para tareas largas (instalaciones, compilaciones)
- Cola de tareas con procesamiento ordenado por chat
- Comandos: `/start`, `/help`, `/status`, `/new`, `/cancel`, `/mc`
- 14 tests automatizados

**Dependencias:** Python 3.12+, FastMCP, httpx, python-dotenv

### 2. WhatsApp MCP (`mcps/whatsapp-mcp/`)

Integración con WhatsApp via bridge (whatsmeow/Go).

**Características:**
- Envío de mensajes de texto, fotos, videos, audio, documentos
- Gestión de chats y contactos
- Descarga de media
- Búsqueda de contactos
- Bridge en Go para conexión multidevice

**Dependencias:** Python 3.11+, Go 1.21+, whatsmeow

### 3. Minecraft MCP (`mcps/minecraft-mcp/`)

Control de servidor Minecraft via RCON.

**Características:**
- 13 herramientas: dar items, teletransportar, clima, tiempo, gamemode, etc.
- Ejecutar cualquier comando del servidor
- Invocar entidades, efectos de poción, localizar estructuras
- Cliente RCON puro en Python (sin dependencias externas)

**Dependencias:** Python 3.10+, FastMCP

## 🔌 Compatibilidad

Los MCPs son **estándar MCP** y funcionan con cualquier cliente compatible:

| Agente | Configuración |
|---|---|
| Claude Desktop | `agents/claude/` |
| Claude Code | `agents/claude-code/` |
| Cursor | `agents/cursor/` |
| Kiro | `agents/kiro/` |
| OpenCode | `agents/opencode/` |
| Windsurf | `agents/windsurf/` |

## ⚡ Instalación rápida

### Requisitos
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- Git

### 1. Clonar

```bash
git clone https://github.com/CRISTOP-bot/mcps-ai.git
cd mcps-ai
```

### 2. Instalar MCPs

```bash
# Telegram
cd mcps/telegram-mcp && uv sync && cp .env.example .env
# Editar .env con tus valores

# WhatsApp
cd mcps/whatsapp-mcp/whatsapp-mcp-server && uv sync

# Minecraft
cd mcps/minecraft-mcp && uv sync && cp .env.example .env
# Editar .env con tus valores
```

### 3. Configurar tu agente

Consulta `agents/<tu-agente>/README.md` o `install.md` para instrucciones detalladas.

### 4. Verificar

```bash
# Telegram
cd mcps/telegram-mcp && uv run python -m pytest tests/ -v

# Minecraft (con mock server)
cd /tmp/opencode && python3 test_rcon_server.py &
cd mcps/minecraft-mcp && uv run python -c "from rcon import RCONClient; r=RCONClient('127.0.0.1',25575,'testpass123'); r.connect(); print(r.command('list')); r.close()"
```

## 📁 Estructura

```
mcps-ai/
├── mcps/                    # Código de los MCP servers
│   ├── telegram-mcp/        # Agente remoto OpenCode-Telegram
│   ├── whatsapp-mcp/        # Integración WhatsApp
│   └── minecraft-mcp/       # Control de Minecraft via RCON
├── agents/                  # Configuraciones por plataforma
│   ├── claude/              # Claude Desktop
│   ├── claude-code/         # Claude Code (CLI)
│   ├── cursor/              # Cursor
│   ├── kiro/                # Kiro
│   ├── opencode/            # OpenCode
│   └── windsurf/            # Windsurf
├── install.md               # Guía para agentes AI
└── README.md
```

## 🔒 Seguridad

- **Nunca** incluir credenciales reales en el repositorio
- Usar archivos `.env` (gitignored) para secretos
- Configurar usuarios autorizados en Telegram (`TELEGRAM_ALLOWED_USERS`)
- OpenCode Server solo escucha en localhost
- No exponer puertos innecesarios

## 🤖 Para agentes AI

Si eres un agente de IA, lee `install.md` para instrucciones detalladas de instalación y configuración.

## 📄 Licencia

MIT — Libre para usar, modificar y distribuir.