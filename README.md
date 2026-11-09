# MCPs para OpenCode

Colección de servidores MCP (Model Context Protocol) para OpenCode.

## MCPs incluidos

### 1. Telegram Remote Agent
Agente remoto de OpenCode controlable via Telegram.
- Worker persistente con long polling
- OpenCode Server integration
- SQLite para persistencia de sesiones
- Auto-cambio de modelo cuando se acaban los tokens
- Sin timeout para tareas largas

**Directorio:** `telegram-mcp/`

### 2. WhatsApp MCP
Integración con WhatsApp via bridge (whatsmeow).
- Envío de mensajes y archivos
- Gestión de chats y contactos
- Descarga de media

**Directorio:** `whatsapp-mcp/`

### 3. Minecraft MCP
Control de servidor Minecraft via RCON.
- 13 herramientas: dar items, teletransportar, clima, tiempo, gamemode, etc.
- Ejecutar cualquier comando del servidor

**Directorio:** `minecraft-mcp/`

## Instalación

Cada MCP tiene su propio README con instrucciones detalladas.

### Requisitos generales
- Python 3.10+
- uv (gestor de paquetes)

### Configuración en OpenCode

Agregar en `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "telegram": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/telegram-mcp", "run", "main.py"],
        "environment": { "TELEGRAM_BOT_TOKEN": "your_token" }
      },
      "whatsapp": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
      },
      "minecraft": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/minecraft-mcp", "run", "main.py"],
        "environment": {
          "MC_HOST": "localhost",
          "MC_PORT": "25575",
          "MC_RCON_PASSWORD": "your_password"
        }
      }
    }
  }
}
```

## Seguridad

- No incluir credenciales reales en el repositorio
- Usar archivos `.env` (gitignored) para secretos
- Configurar usuarios autorizados en Telegram

## Licencia

MIT
PYEOF
echo "README principal creado"