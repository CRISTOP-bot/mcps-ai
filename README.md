# MCPs para IA

> Colección de servidores MCP (Model Context Protocol) universales para agentes de IA.

[![GitHub](https://img.shields.io/badge/GitHub-mcps--ai-blue?logo=github)](https://github.com/CRISTOP-bot/mcps-ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Tabla de contenidos

- [MCPs incluidos](#mcps-incluidos)
- [Compatibilidad](#compatibilidad)
- [Estructura](#estructura)
- [Instalación rápida](#instalación-rápida)
- [Seguridad](#seguridad)
- [Licencia](#licencia)

## 🧩 MCPs incluidos

### 1. Telegram Remote Agent (`mcps/telegram-mcp/`)
Agente remoto de IA controlable via Telegram.
- Worker persistente con long polling (24/7)
- Integración con AI Server API
- SQLite para persistencia de sesiones y tareas
- Auto-cambio de modelo cuando se acaban los tokens (11 modelos de respaldo)
- Sin timeout para tareas largas
- 14 tests automatizados

### 2. WhatsApp MCP (`mcps/whatsapp-mcp/`)
Integración con WhatsApp via bridge (whatsmeow/Go).
- Envío de mensajes de texto, fotos, videos, audio, documentos
- Gestión de chats y contactos
- Descarga de media

### 3. Minecraft MCP (`mcps/minecraft-mcp/`)
Control de servidor Minecraft via RCON.
- 13 herramientas: dar items, teletransportar, clima, tiempo, gamemode, etc.
- Ejecutar cualquier comando del servidor
- 4 tests automatizados

## 🔌 Compatibilidad

Cada agente tiene su propia copia de los MCPs en `agents/<agente>/mcps/`:

| Agente | Directorio | Configuración |
|---|---|---|
| Claude Desktop | `agents/claude/` | `agents/claude/README.md` |
| Claude Code | `agents/claude-code/` | `agents/claude-code/README.md` |
| Cursor | `agents/cursor/` | `agents/cursor/README.md` |
| Kiro | `agents/kiro/` | `agents/kiro/README.md` |
| OpenClaw | `agents/openclaw/` | `agents/openclaw/README.md` |
| OpenCode | `agents/opencode/` | `agents/opencode/README.md` |
| Windsurf | `agents/windsurf/` | `agents/windsurf/README.md` |

## 📁 Estructura

```
mcps-ai/
├── mcps/                    # Código fuente de los MCPs
│   ├── telegram-mcp/
│   ├── whatsapp-mcp/
│   └── minecraft-mcp/
├── agents/                  # MCPs + config por agente
│   ├── claude/mcps/         # Copia para Claude Desktop
│   ├── claude-code/mcps/    # Copia para Claude Code
│   ├── cursor/mcps/         # Copia para Cursor
│   ├── kiro/mcps/           # Copia para Kiro
│   ├── openclaw/mcps/       # Copia para OpenClaw
│   ├── opencode/mcps/       # Copia para OpenCode
│   └── windsurf/mcps/       # Copia para Windsurf
├── install.md               # Guía para agentes AI
├── setup.sh                 # Script de instalación
└── README.md
```

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

### 2. Elegir tu agente

Cada agente tiene sus MCPs en `agents/<agente>/mcps/`. Consulta `agents/<agente>/README.md` para configuración específica.

### 3. Instalar dependencias

```bash
# Telegram
cd agents/<agente>/mcps/telegram-mcp && uv sync && cp .env.example .env

# WhatsApp
cd agents/<agente>/mcps/whatsapp-mcp/whatsapp-mcp-server && uv sync

# Minecraft
cd agents/<agente>/mcps/minecraft-mcp && uv sync && cp .env.example .env
```

### 4. Editar .env con tus valores

## 🔒 Seguridad

- **Nunca** incluir credenciales reales en el repositorio
- Usar archivos `.env` (gitignored) para secretos
- Configurar usuarios autorizados en Telegram

## 🤖 Para agentes AI

Si eres un agente de IA, lee `install.md` para instrucciones detalladas de instalación y configuración.

## 📄 Licencia

MIT — Libre para usar, modificar y distribuir.