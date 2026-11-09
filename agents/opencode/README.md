# OpenCode Configuration

Edita `~/.config/opencode/opencode.json` y agrega:

```json
{
  "mcp": {
    "servers": {
      "telegram": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/telegram-mcp", "run", "main.py"],
        "environment": { "TELEGRAM_BOT_TOKEN": "your_token" }
      },
      "whatsapp": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
      },
      "minecraft": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/minecraft-mcp", "run", "main.py"],
        "environment": {
          "MC_HOST": "localhost",
          "MC_PORT": "25575",
          "MC_RCON_PASSWORD": "your_password"
        }
      },
      "gmail": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/gmail-mcp", "run", "main.py"],
        "environment": {
          "GMAIL_CREDENTIALS": "~/.mcps-ai/repo/mcps/gmail-mcp/credentials.json",
          "GMAIL_TOKEN": "~/.mcps-ai/repo/mcps/gmail-mcp/token.json"
        }
      },
      "filesystem": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/filesystem-mcp", "run", "main.py"]
      },
      "system": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/system-mcp", "run", "main.py"]
      },
      "web": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/web-mcp", "run", "main.py"]
      },
      "browser": {
        "type": "local",
        "command": ["uv", "--directory", "~/.mcps-ai/repo/mcps/browser-mcp", "run", "main.py"]
      }
    }
  }
}
```

`~` se expande automáticamente. O usa la ruta completa.

## Telegram Worker (servicio systemd)

```bash
systemctl --user enable --now opencode-telegram-worker
```

## macOS

Usa los plists de launchd incluidos en `mcps/telegram-mcp/`:

```bash
cp mcps/telegram-mcp/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cristopher.opencode-server.plist
launchctl load ~/Library/LaunchAgents/com.cristopher.telegram-worker.plist
```
