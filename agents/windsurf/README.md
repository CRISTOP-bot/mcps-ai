# Windsurf Configuration

## ~/.codeium/windsurf/mcp_config.json

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/windsurf/mcps/telegram-mcp", "run", "main.py"],
      "env": { "TELEGRAM_BOT_TOKEN": "your_token" }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/windsurf/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/windsurf/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "your_password"
      }
    }
  }
}
```
EOF
echo "windsurf config creado"
## Gmail MCP

```json
{
  "gmail": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/windsurf/mcps/gmail-mcp", "run", "main.py"],
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
    "args": ["--directory", "/path/to/agents/windsurf/mcps/filesystem-mcp", "run", "main.py"]
  }
}
```

## System MCP

```json
{
  "system": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/windsurf/mcps/system-mcp", "run", "main.py"]
  }
}
```

## macOS
Usa los plists de launchd incluidos en `telegram-mcp/` (en vez de systemd):
```bash
cp telegram-mcp/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cristopher.opencode-server.plist
launchctl load ~/Library/LaunchAgents/com.cristopher.telegram-worker.plist
```
