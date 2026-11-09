# OpenCode Configuration

## opencode.json

Ubicación: `~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "servers": {
      "telegram": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/agents/opencode/mcps/telegram-mcp", "run", "main.py"],
        "environment": { "TELEGRAM_BOT_TOKEN": "your_token" }
      },
      "whatsapp": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/agents/opencode/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
      },
      "minecraft": {
        "type": "local",
        "command": ["/path/to/uv", "--directory", "/path/to/agents/opencode/mcps/minecraft-mcp", "run", "main.py"],
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

## OpenCode Server (para Telegram Remote Agent)

```bash
opencode serve --port 4096 --hostname 127.0.0.1
```

## Telegram Worker (servicio systemd)

```bash
systemctl --user enable --now opencode-telegram-worker
```
PYEOF
echo "opencode config creado"