# Claude Code Configuration

## .mcp.json (en la raíz del proyecto o ~/.claude/.mcp.json)

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude-code/mcps/telegram-mcp", "run", "main.py"],
      "env": { "TELEGRAM_BOT_TOKEN": "your_token" }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude-code/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude-code/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "your_password"
      }
    }
  }
}
```

## Instalación via CLI

```bash
claude mcp add telegram -- uv --directory /path/to/agents/claude-code/mcps/telegram-mcp run main.py
claude mcp add whatsapp -- uv --directory /path/to/agents/claude-code/mcps/whatsapp-mcp/whatsapp-mcp-server run main.py
claude mcp add minecraft -- uv --directory /path/to/agents/claude-code/mcps/minecraft-mcp run main.py
```

## Verificar conexión

```bash
claude mcp list
```

## Gmail MCP

```json
{
  "gmail": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/claude-code/mcps/gmail-mcp", "run", "main.py"],
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
    "args": ["--directory", "/path/to/agents/claude-code/mcps/filesystem-mcp", "run", "main.py"]
  }
}
```

## System MCP

```json
{
  "system": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/claude-code/mcps/system-mcp", "run", "main.py"]
  }
}
```
