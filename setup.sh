#!/bin/bash
# Setup script for mcps-ai

set -e

echo "=== MCPs AI Setup ==="
echo ""

# Check uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install it first."
    exit 1
fi

echo "Setting up Telegram MCP..."
cd mcps/telegram-mcp
uv sync
cp -n .env.example .env 2>/dev/null || true
cd ../..

echo "Setting up WhatsApp MCP..."
cd mcps/whatsapp-mcp/whatsapp-mcp-server
uv sync
cd ../../..

echo "Setting up Minecraft MCP..."
cd mcps/minecraft-mcp
uv sync
cp -n .env.example .env 2>/dev/null || true
cd ../..

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Edit mcps/telegram-mcp/.env with your Telegram bot token"
echo "2. Edit mcps/minecraft-mcp/.env with your Minecraft RCON password"
echo "3. Configure your agent (see agents/<your-agent>/README.md)"
echo "4. For Telegram remote agent: start IA server and telegram worker"
EOF
chmod +x /tmp/mcps-ai/setup.sh
echo "setup.sh creado"