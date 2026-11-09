#!/bin/bash
# Setup script for mcps-ai (Linux, macOS)

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

echo "Setting up Telegram MCP..."
cd agents/${1:-opencode}/mcps/telegram-mcp
uv sync
cp -n .env.example .env 2>/dev/null || true
cd - > /dev/null

echo "Setting up WhatsApp MCP..."
cd agents/${1:-opencode}/mcps/whatsapp-mcp/whatsapp-mcp-server
uv sync
cd - > /dev/null

echo "Setting up Minecraft MCP..."
cd agents/${1:-opencode}/mcps/minecraft-mcp
uv sync
cp -n .env.example .env 2>/dev/null || true
cd - > /dev/null

echo "Setting up Gmail MCP..."
cd agents/${1:-opencode}/mcps/gmail-mcp
uv sync
cp -n .env.example .env 2>/dev/null || true
cd - > /dev/null

echo "Setting up Filesystem MCP..."
cd agents/${1:-opencode}/mcps/filesystem-mcp
uv sync
cd - > /dev/null

echo "Setting up System MCP..."
cd agents/${1:-opencode}/mcps/system-mcp
uv sync
cd - > /dev/null

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Edit agents/${1:-opencode}/mcps/telegram-mcp/.env with your Telegram bot token"
echo "2. Edit agents/${1:-opencode}/mcps/minecraft-mcp/.env with your Minecraft RCON password"
echo "3. Edit agents/${1:-opencode}/mcps/gmail-mcp/.env and download credentials.json"
echo "4. Configure your agent (see agents/<agent>/README.md)"
if [ "$OS" = "Darwin" ]; then
    echo "5. macOS: Copy plists from agents/${1:-opencode}/mcps/telegram-mcp/*.plist to ~/Library/LaunchAgents/"
else
    echo "5. Linux: systemctl --user enable --now opencode-telegram-worker"
fi
