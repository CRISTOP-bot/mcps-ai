# Claude Code Configuration

Edita `.mcp.json (en la raíz del proyecto)` y agrega:

```json
{
  mcpServers: {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/telegram-mcp", "run", "main.py"],
      "env": { "TELEGRAM_BOT_TOKEN": "your_token" }
    },
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/whatsapp-mcp/whatsapp-mcp-server", "run", "main.py"]
    },
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/minecraft-mcp", "run", "main.py"],
      "env": {
        "MC_HOST": "localhost",
        "MC_PORT": "25575",
        "MC_RCON_PASSWORD": "your_password"
      }
    },
    "gmail": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/gmail-mcp", "run", "main.py"],
      "env": {
        "GMAIL_CREDENTIALS": "~/.mcps-ai/repo/mcps/gmail-mcp/credentials.json",
        "GMAIL_TOKEN": "~/.mcps-ai/repo/mcps/gmail-mcp/token.json"
      }
    },
    "filesystem": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/filesystem-mcp", "run", "main.py"]
    },
    "system": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/system-mcp", "run", "main.py"]
    },
    "web": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/web-mcp", "run", "main.py"]
    },
    "browser": {
      "command": "uv",
      "args": ["--directory", "~/.mcps-ai/repo/mcps/browser-mcp", "run", "main.py"]
    }
  }
}
```

`~` se expande automáticamente. O usa rutas absolutas.

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
