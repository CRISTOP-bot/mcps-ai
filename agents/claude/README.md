# Claude Desktop / Claude Code Configuration

## Claude Desktop (claude_desktop_config.json)

Ubicación: `~/.config/claude/claude_desktop_config.json` (Linux) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude/mcps/telegram-mcp", "run", "main.py"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_token_here"
      }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "your_password"
      }
    }
  }
}
```

## Claude Code (.mcp.json)

Ubicación: raíz del proyecto o `~/.claude/.mcp.json`

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/claude/mcps/telegram-mcp", "run", "main.py"],
      "env": { "TELEGRAM_BOT_TOKEN": "your_token" }
    }
  }
}
```
PYEOF
echo "claude config creado"
## Gmail MCP

```json
{
  "gmail": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/claude/mcps/gmail-mcp", "run", "main.py"],
    "env": {
      "GMAIL_CREDENTIALS": "/path/to/credentials.json",
      "GMAIL_TOKEN": "/path/to/token.json"
    }
  }
}
```

Requiere autenticacion OAuth2 (ver gmail-mcp/README.md).
