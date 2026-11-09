# Kiro Configuration

## Kiro MCP Config

Ubicación: `~/.kiro/settings/mcp.json` o `.kiro/settings/mcp.json` en el proyecto

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/kiro/mcps/telegram-mcp", "run", "main.py"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_token"
      }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/kiro/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/path/to/agents/kiro/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "your_password"
      }
    }
  }
}
```

## Notas
- Kiro usa el mismo formato que Claude Desktop (mcpServers)
- Los MCPs son compatibles con cualquier cliente MCP estándar
PYEOF
echo "kiro config creado"
## Gmail MCP

```json
{
  "gmail": {
    "command": "uv",
    "args": ["--directory", "/path/to/agents/kiro/mcps/gmail-mcp", "run", "main.py"],
    "env": {
      "GMAIL_CREDENTIALS": "/path/to/credentials.json",
      "GMAIL_TOKEN": "/path/to/token.json"
    }
  }
}
```

Requiere autenticacion OAuth2 (ver gmail-mcp/README.md).
