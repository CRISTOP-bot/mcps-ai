# discord-mcp

MCP server for interacting with Discord via the REST API. Supports bot-token auth for most tools and an optional webhook URL for simple message sending.

## Setup

1. Create a Discord application and bot:
   - Go to https://discord.com/developers/applications and click **New Application**.
   - Open the **Bot** tab, click **Add Bot**, then copy the bot token.
   - Enable the **Message Content Intent** under **Privileged Gateway Intents** (required to read message content). Enable **Server Members Intent** if you want `discord_list_members` to work.
2. Invite the bot to your server:
   - Go to **OAuth2 → URL Generator**.
   - Scopes: `bot`.
   - Bot permissions: **Send Messages**, **Read Message History**, **Manage Channels**, **Add Reactions** (and **View Channels**).
   - Open the generated URL and authorize the bot for your guild.
3. Copy the token into `.env`:
   ```
   cp .env.example .env
   # edit .env and set DISCORD_BOT_TOKEN=your-token-here
   ```
4. (Optional) Webhook alternative for `discord_send_webhook`:
   - In a channel: **Edit Channel → Integrations → Webhooks → New Webhook**, copy the webhook URL.
   - Set `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...` in `.env`.

## Running

```
uv sync
uv run python main.py
```

The server runs over stdio. Add it to your MCP client config, e.g.:

```json
{
  "mcpServers": {
    "discord": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/discord-mcp", "python", "main.py"]
    }
  }
}
```

## Environment variables

- `DISCORD_BOT_TOKEN` — bot token used for the Discord REST API (`Authorization: Bot <token>`). Required for all tools except `discord_send_webhook`.
- `DISCORD_WEBHOOK_URL` — optional webhook URL used only by `discord_send_webhook`.

## Tools

See the tool list in the source (`main.py`). All tools return dicts; errors are returned as `{"error": "..."}` and never raised.
