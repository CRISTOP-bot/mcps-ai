# OpenClaw Configuration

## openclaw.json (o ~/.openclaw/config.json)

```json5
{
  mcp: {
    servers: {
      telegram: {
        command: "uv",
        args: ["--directory", "/path/to/mcps/telegram-mcp", "run", "main.py"],
        env: { TELEGRAM_BOT_TOKEN: "your_token" },
      },
      whatsapp: {
        command: "uv",
        args: ["--directory", "/path/to/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"],
      },
      minecraft: {
        command: "uv",
        args: ["--directory", "/path/to/mcps/minecraft-mcp", "run", "main.py"],
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
openclaw mcp add telegram --command uv --arg --directory --arg /path/to/mcps/telegram-mcp --arg run --arg main.py
openclaw mcp add whatsapp --command uv --arg --directory --arg /path/to/mcps/whatsapp-mcp/whatsapp-mcp-server --arg run --arg main.py
openclaw mcp add minecraft --command uv --arg --directory --arg /path/to/mcps/minecraft-mcp --arg run --arg main.py

# Verificar
openclaw mcp doctor telegram --probe
openclaw mcp status --verbose
```

## Notas
- OpenClaw soporta stdio, SSE y Streamable HTTP
- Los MCPs de este repo usan stdio (command-based)
- OpenClaw puede ejecutar MCPs en nodos remotos (node-hosted)
