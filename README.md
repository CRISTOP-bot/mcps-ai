# MCPs para OpenCode

Colección de servidores MCP (Model Context Protocol) compatibles con múltiples agentes.

## Estructura

```
mcps-opencode/
├── mcps/                    # Código de los MCP servers
│   ├── telegram-mcp/        # Agente remoto OpenCode-Telegram
│   ├── whatsapp-mcp/        # Integración WhatsApp
│   └── minecraft-mcp/       # Control de Minecraft via RCON
├── agents/                  # Configuraciones por plataforma
│   ├── claude/              # Claude Desktop / Claude Code
│   ├── opencode/            # OpenCode
│   └── kiro/                # Kiro
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
- **Claude Desktop** / **Claude Code** → ver `agents/claude/`
- **OpenCode** → ver `agents/opencode/`
- **Kiro** → ver `agents/kiro/`
- Cualquier cliente MCP compatible

## Instalación

Cada MCP tiene su propio README con instrucciones detalladas.

### Requisitos generales
- Python 3.10+
- uv (gestor de paquetes)

## Seguridad

- No incluir credenciales reales en el repositorio
- Usar archivos `.env` (gitignored) para secretos
- Configurar usuarios autorizados en Telegram

## Licencia

MIT
PYEOF
echo "README actualizado"