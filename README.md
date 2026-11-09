# MCPs para OpenCode

Colección de servidores MCP (Model Context Protocol) compatibles con múltiples agentes y plataformas.

## Estructura

```
mcps-opencode/
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
└── README.md
```

## MCPs incluidos

### 1. Telegram Remote Agent (`mcps/telegram-mcp/`)
Agente remoto de OpenCode controlable via Telegram.
- Worker persistente con long polling
- SQLite para persistencia de sesiones
- Auto-cambio de modelo cuando se acaban los tokens
- Sin timeout para tareas largas
- 14 tests automatizados
- Comandos: /start, /help, /status, /new, /cancel, /mc

### 2. WhatsApp MCP (`mcps/whatsapp-mcp/`)
Integración con WhatsApp via bridge (whatsmeow).
- Envío de mensajes y archivos
- Gestión de chats y contactos
- Descarga de media

### 3. Minecraft MCP (`mcps/minecraft-mcp/`)
Control de servidor Minecraft via RCON.
- 13 herramientas: dar items, teletransportar, clima, tiempo, gamemode, etc.
- Ejecutar cualquier comando del servidor

## Compatibilidad

Los MCPs son **estándar MCP** y funcionan con:
- **Claude Desktop** → `agents/claude/`
- **Claude Code** → `agents/claude-code/`
- **Cursor** → `agents/cursor/`
- **Kiro** → `agents/kiro/`
- **OpenCode** → `agents/opencode/`
- **Windsurf** → `agents/windsurf/`
- Cualquier cliente MCP compatible

## Instalación

Cada MCP tiene su propio README con instrucciones detalladas.

### Requisitos generales
- Python 3.10+
- uv (gestor de paquetes)

### Setup rápido

```bash
# Clonar repo
git clone https://github.com/CRISTOP-bot/mcps-opencode.git
cd mcps-opencode

# Telegram MCP
cd mcps/telegram-mcp && uv sync && cp .env.example .env
# Editar .env con tus valores

# WhatsApp MCP
cd mcps/whatsapp-mcp/whatsapp-mcp-server && uv sync

# Minecraft MCP
cd mcps/minecraft-mcp && uv sync && cp .env.example .env
# Editar .env con tus valores
```

## Seguridad

- No incluir credenciales reales en el repositorio
- Usar archivos `.env` (gitignored) para secretos
- Configurar usuarios autorizados en Telegram

## Licencia

MIT
PYEOF
echo "README actualizado"