# INSTALL.md - Guía de instalación para agentes AI

Este archivo está diseñado para ser leído por agentes de IA (Claude, OpenCode, Kiro, Cursor, Windsurf, OpenClaw, etc.) para instalar y configurar los MCPs de este repositorio.

## Instrucciones para el agente AI

Si el usuario te pide instalar los MCPs de este repositorio, sigue estos pasos:

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/CRISTOP-bot/mcps-ai.git
cd mcps-ai
```

### Paso 2: Identificar el agente/cliente del usuario

Pregunta al usuario qué agente usa o detecta automáticamente:
- OpenCode → config en `~/.config/opencode/opencode.json`
- Claude Desktop → `~/.config/claude/claude_desktop_config.json`
- Claude Code → `.mcp.json` en la raíz del proyecto
- Kiro → `~/.kiro/settings/mcp.json`
- Cursor → `.cursor/mcp.json`
- Windsurf → `~/.codeium/windsurf/mcp_config.json`
- OpenClaw → `~/.openclaw/config.json` o `openclaw.json`

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

**Filesystem MCP:**
```bash
cd agents/<agente>/mcps/filesystem-mcp
uv sync
```

**System MCP:**
```bash
cd agents/<agente>/mcps/system-mcp
uv sync
```

**Browser MCP:**
```bash
cd agents/<agente>/mcps/browser-mcp
uv sync
uv run playwright install chromium
```

**Web MCP:**
```bash
cd agents/<agente>/mcps/web-mcp
uv sync
```

**Minecraft MCP:**
```bash
cd mcps/minecraft-mcp
uv sync
cp .env.example .env
# Editar .env con los valores del usuario
```

### Paso 3.5 (solo macOS): Instalar servicios con launchd

```bash
cp agents/<agente>/mcps/telegram-mcp/com.cristopher.opencode-server.plist ~/Library/LaunchAgents/
cp agents/<agente>/mcps/telegram-mcp/com.cristopher.telegram-worker.plist ~/Library/LaunchAgents/
# Edita USERNAME y OPENCODE_SERVER_PASSWORD en ambos plists
launchctl load ~/Library/LaunchAgents/com.cristopher.opencode-server.plist
launchctl load ~/Library/LaunchAgents/com.cristopher.telegram-worker.plist
```

Nota: En macOS los comandos de systemd no funcionan; usa launchctl.

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
    },
    "filesystem": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE_PATH/mcps/filesystem-mcp", "run", "main.py"]
    },
    "system": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE_PATH/mcps/system-mcp", "run", "main.py"]
    }
  }
}
```

### Paso 5: Variables de entorno necesarias

**Telegram MCP (.env):**
- TELEGRAM_BOT_TOKEN (de @BotFather)
- TELEGRAM_ALLOWED_USERS (IDs de Telegram, separados por coma)
- AI_BASE_URL (http://127.0.0.1:4096)
- AI_PASSWORD (de service.json de OpenCode)
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
# OpenCode Server
opencode serve --port 4096 --hostname 127.0.0.1

# Telegram Worker (en otra terminal)
cd mcps/telegram-mcp && uv run python telegram_worker.py

# O como servicio systemd
systemctl --user enable --now opencode-telegram-worker
```

### Paso 7: Verificar

```bash
# Verificar OpenCode Server
curl -u opencode:PASSWORD http://127.0.0.1:4096/api/info

# Verificar MCPs registrados
# (depende del agente: claude mcp list, opencode mcp list, etc.)
```

## Notas para el agente AI

1. **No inventar credenciales** - Siempre pedir al usuario sus tokens/passwords
2. **No exponer secrets** - Usar archivos .env (gitignored) para secretos
3. **Paths absolutos** - Usar rutas absolutas en la configuración
4. **Verificar dependencias** - Asegurar que uv, python, java (para Minecraft) estén instalados
5. **Los MCPs son universales** - El mismo código funciona con cualquier cliente MCP
6. **No modificar el código fuente** sin autorización del usuario

## Arquitectura universal

Los MCPs usan el protocolo estándar MCP (stdio transport), por lo que son compatibles con:
- Claude Desktop
- Claude Code
- OpenCode
- Kiro
- Cursor
- Windsurf
- Cline
- Continue
- Zed
- OpenClaw
- Y cualquier cliente MCP estándar

La única diferencia entre agentes es el **formato del archivo de configuración**, no el código del MCP.
EOF
echo "install.md reescrito"