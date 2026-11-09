#!/bin/bash
# Setup script for mcps-ai (Linux, macOS)
# Installs all Python deps, seeds .env files, and auto-configures what's trivial.

set -e

echo "=== MCPs AI Setup ==="

# Detect OS
OS="$(uname -s)"
echo "Detected OS: $OS"

# Check uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install it first."
    if [ "$OS" = "Darwin" ]; then
        echo "  macOS: brew install python3"
    else
        echo "  Debian/Ubuntu: sudo apt install python3"
    fi
    exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- Install Python deps for every MCP (canonical mcps/ dir) ---
for dir in "$ROOT"/mcps/*/; do
    name=$(basename "$dir")
    # WhatsApp server lives one level deeper
    target="$dir"
    [ "$name" = "whatsapp-mcp" ] && target="$dir/whatsapp-mcp-server"
    if [ -f "$target/pyproject.toml" ]; then
        echo "Setting up $name..."
        (cd "$target" && uv sync) || echo "  (deps failed for $name, continuing)"
        if [ ! -f "$target/.env" ] && [ -f "$target/.env.example" ]; then
            cp "$target/.env.example" "$target/.env"
        fi
    fi
done

# --- Auto-configure what's trivial (never overwrites existing .env) ---
echo ""
echo "=== Auto-configuración ==="

# GitHub: token from gh CLI
if [ ! -f "$ROOT/mcps/github-mcp/.env" ] && command -v gh &> /dev/null; then
    if TOKEN="$(gh auth token 2>/dev/null)" && [ -n "$TOKEN" ]; then
        printf 'GITHUB_TOKEN=%s\n' "$TOKEN" > "$ROOT/mcps/github-mcp/.env"
        chmod 600 "$ROOT/mcps/github-mcp/.env"
        echo "  ✓ github (token desde gh CLI)"
    fi
fi

# Orchestrator: reuse AI_* from an existing telegram-mcp .env
if [ ! -f "$ROOT/mcps/orchestrator-mcp/.env" ]; then
    for SRC in "$ROOT/mcps/telegram-mcp/.env" "$HOME/mcp-servers/telegram-mcp/.env"; do
        if [ -f "$SRC" ] && grep -qE '^AI_(BASE_URL|PASSWORD)=' "$SRC"; then
            ( umask 077; { grep -E '^AI_(BASE_URL|PASSWORD|AUTH_USER|DIRECTORY|MODEL_ID|MODEL_PROVIDER)=' "$SRC"
              echo 'REQUEST_TIMEOUT=0'
              echo 'DATABASE_PATH=./data/orchestra.db'; } > "$ROOT/mcps/orchestrator-mcp/.env" )
            echo "  ✓ orchestrator (AI_* reutilizado de $SRC)"
            break
        fi
    done
fi

# Browser: install chromium for Playwright if not cached
if [ ! -d "$HOME/.cache/ms-playwright" ] && [ -d "$ROOT/mcps/browser-mcp" ]; then
    echo "  Instalando Playwright chromium (puede tardar 1-2 min)..."
    (cd "$ROOT/mcps/browser-mcp" && uv run playwright install chromium) \
        && echo "  ✓ browser (chromium instalado)" \
        || echo "  ⚠ browser (falló; ejecuta: cd mcps/browser-mcp && uv run playwright install chromium)"
fi

# Home Assistant: detect reachable instance (URL only)
if [ ! -f "$ROOT/mcps/homeassistant-mcp/.env" ] && command -v curl &> /dev/null; then
    for URL in http://homeassistant.local:8123 http://127.0.0.1:8123; do
        if curl -fsS -m 2 "$URL/api/" > /dev/null 2>&1; then
            printf 'HA_URL=%s\nHA_TOKEN=\n' "$URL" > "$ROOT/mcps/homeassistant-mcp/.env"
            chmod 600 "$ROOT/mcps/homeassistant-mcp/.env"
            echo "  ✓ homeassistant (instancia detectada en $URL; falta HA_TOKEN)"
            break
        fi
    done
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Edit mcps/telegram-mcp/.env with your Telegram bot token (si usas Telegram)"
echo "2. Edit mcps/minecraft-mcp/.env with your Minecraft RCON password (si usas Minecraft)"
echo "3. Para Gmail: coloca credentials.json en mcps/gmail-mcp/ y ejecuta: cd mcps/gmail-mcp && uv run python gmail_auth.py"
echo "4. El Orchestrator ya funciona si tu OpenCode Server está corriendo (127.0.0.1:4096)"
echo "5. GitHub, Discord, Slack, Spotify, Notion: coloca tokens en su .env si los quieres usar"
echo "6. Configura tu agente (ver README.md o wiki)"
if [ "$OS" = "Darwin" ]; then
    echo "7. macOS: copia los plists de mcps/telegram-mcp/*.plist a ~/Library/LaunchAgents/"
else
    echo "7. Linux: systemctl --user enable --now opencode-telegram-worker"
fi
