# OpenClaw Configuration

## openclaw.json (o ~/.openclaw/config.json)

```json5
{
  mcp: {
    servers: {
      telegram: {
        command: "uv",
        args: ["--directory", "/path/to/agents/openclaw/mcps/telegram-mcp", "run", "main.py"],
        env: { TELEGRAM_BOT_TOKEN: "your_token" },
      },
      whatsapp: {
        command: "uv",
        args: ["--directory", "/path/to/agents/openclaw/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"],
      },
      minecraft: {
        command: "uv",
        args: ["--directory", "/path/to/agents/openclaw/mcps/minecraft-mcp", "run", "main.py"],
        env: {
          MC_HOST: "localhost",
          MC_PORT: "25575",
          MC_RCON_PASSWORD: "your_password",
        },
      },
    },
  },
}
```

## CLI

```bash
openclaw mcp add telegram --command uv --arg --directory --arg /path/to/agents/openclaw/mcps/telegram-mcp --arg run --arg main.py
openclaw mcp add whatsapp --command uv --arg --directory --arg /path/to/agents/openclaw/mcps/whatsapp-mcp/whatsapp-mcp-server --arg run --arg main.py
openclaw mcp add minecraft --command uv --arg --directory --arg /path/to/agents/openclaw/mcps/minecraft-mcp --arg run --arg main.py

# Verificar
openclaw mcp doctor telegram --probe
openclaw mcp status --verbose
```

## Notas
- OpenClaw soporta stdio, SSE y Streamable HTTP
- Los MCPs de este repo usan stdio (command-based)
- OpenClaw puede ejecutar MCPs en nodos remotos (node-hosted)

## Gmail MCP

```json
{
  "gmail": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/openclaw/mcps/gmail-mcp", "run", "main.py"],
    "env": {
      "GMAIL_CREDENTIALS": "/path/to/credentials.json",
      "GMAIL_TOKEN": "/path/to/token.json"
    }
  }
}
```

Requiere autenticacion OAuth2 (ver gmail-mcp/README.md).

## Filesystem MCP

```json
{
  "filesystem": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/openclaw/mcps/filesystem-mcp", "run", "main.py"]
  }
}
```

## System MCP

```json
{
  "system": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/openclaw/mcps/system-mcp", "run", "main.py"]
  }
}
```
