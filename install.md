# INSTALL.md - Guía de instalación para agentes AI

Este archivo está diseñado para ser leído por agentes de IA (Claude, IA, Kiro, Cursor, Windsurf, etc.) para instalar y configurar los MCPs de este repositorio.

## Instrucciones para el agente AI

Si el usuario te pide instalar los MCPs de este repositorio, sigue estos pasos:

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/CRISTOP-bot/mcps-ai.git
cd mcps-ai
```

### Paso 2: Identificar el agente/cliente del usuario

Pregunta al usuario qué agente usa o detecta automáticamente:
- IA → config en `~/.config/ai/ai.json`
- Claude Desktop → `~/.config/claude/claude_desktop_config.json`
- Claude Code → `.mcp.json` en la raíz del proyecto
- Kiro → `~/.kiro/settings/mcp.json`
- Cursor → `.cursor/mcp.json`
- Windsurf → `~/.codeium/windsurf/mcp_config.json`

### Paso 3: Instalar dependencias

Para cada MCP que el usuario quiera:

**Telegram MCP:**
```bash
cd mcps/telegram-mcp
uv sync
cp .env.example .env
# Editar .env con los valores del usuario
```

**WhatsApp MCP:**
```bash
cd mcps/whatsapp-mcp/whatsapp-mcp-server
uv sync
```

**Minecraft MCP:**
```bash
cd mcps/minecraft-mcp
uv sync
cp .env.example .env
# Editar .env con los valores del usuario
```

### Paso 4: Configurar el agente

Usa la configuración del directorio `agents/<agente>/README.md` correspondiente.

Formato universal para cualquier agente MCP:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE_PATH/mcps/telegram-mcp", "run", "main.py"],
      "env": { "TELEGRAM_BOT_TOKEN": "TOKEN" }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE_PATH/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE_PATH/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "PASSWORD"
      }
    }
  }
}
```

### Paso 5: Variables de entorno necesarias

**Telegram MCP (.env):**
- TELEGRAM_BOT_TOKEN (de @BotFather)
- TELEGRAM_ALLOWED_USERS (IDs de Telegram, separados por coma)
- AI_BASE_URL (http://127.0.0.1:4096)
- AI_PASSWORD (de service.json de IA)
- AI_DIRECTORY (directorio de trabajo)
- DATABASE_PATH (./data/telegram.db)

**Minecraft MCP (.env):**
- MC_HOST (localhost)
- MC_PORT (25575)
- MC_RCON_PASSWORD (password de RCON del servidor)
- MC_PLAYER (tu username de Minecraft)

**WhatsApp MCP:**
- No requiere .env, pero necesita el bridge compilado (Go)

### Paso 6: Iniciar servicios (solo Telegram Remote Agent)

```bash
# IA Server
ai serve --port 4096 --hostname 127.0.0.1

# Telegram Worker (en otra terminal)
cd mcps/telegram-mcp && uv run python telegram_worker.py

# O como servicio systemd
systemctl --user enable --now ai-telegram-worker
```

### Paso 7: Verificar

```bash
# Verificar IA Server
curl -u ai:PASSWORD http://127.0.0.1:4096/api/info

# Verificar MCPs registrados
# (depende del agente: claude mcp list, ai mcp list, etc.)
```

## Notas para el agente AI

1. **No inventar credenciales** - Siempre pedir al usuario sus tokens/passwords
2. **No exponer secrets** - Usar archivos .env (gitignored)
3. **Paths absolutos** - Usar rutas absolutas en la configuración
4. **Verificar dependencias** - Asegurar que uv, python, java (para Minecraft) estén instalados
5. **Los MCPs son universales** - El mismo código funciona con cualquier cliente MCP
6. **No modificar el código fuente** sin autorización del usuario

## Arquitectura universal

Los MCPs usan el protocolo estándar MCP (stdio transport), por lo que son compatibles con:
- Claude Desktop
- Claude Code
- IA
- Kiro
- Cursor
- Windsurf
- Cline
- Continue
- Zed
- Y cualquier cliente MCP estándar

La única diferencia entre agentes es el **formato del archivo de configuración**, no el código del MCP.
EOF
echo "install.md creado"