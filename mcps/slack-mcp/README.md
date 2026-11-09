# slack-mcp

Slack MCP server built with FastMCP. Talks to the Slack Web API using `urllib` (no extra HTTP deps).

## Setup

1. Create a Slack app at https://api.slack.com/apps (e.g. "From scratch").
2. Under **OAuth & Permissions → Bot Token Scopes**, add:
   - `chat:write`
   - `channels:read`
   - `channels:history`
   - `groups:read`
   - `groups:history`
   - `im:write`
   - `reactions:write`
   - `pins:write`
   - `users:read`
   - `search:read` (**user token only** — see below)
3. Install the app to your workspace (**Install to Workspace**).
4. Copy the **Bot User OAuth Token** (`xoxb-...`) into a `.env` file next to `main.py`:

   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

5. Run:

   ```
   uv sync
   uv run python main.py
   ```

## Notes

- `slack_search_messages` uses `search.messages`, which normally requires a **user token** (`xoxp-...`) with the `search:read` scope. Bot tokens will typically fail with `missing_scope`; the error dict is returned as-is.
- Write methods send a JSON body (`{"channel": ...}`), which Slack supports for `chat.postMessage`, `conversations.open`, `reactions.add`, `pins.add`. GET-ish methods (`conversations.list`, `conversations.history`, `users.list`, `auth.test`, `conversations.info`, `users.info`) use query params.
- All tools return compact dicts and never raise; Slack API failures come back as `{"error": "..."}`.

## Tools

- `slack_auth_test()` — who am I (team/user/bot_id); useful for setup checks
- `slack_send_message(channel, text)` — post a message to a channel (ID or #name)
- `slack_send_dm(user_id, text)` — open a DM and send a message
- `slack_list_channels(limit=50, channel_type="public_channel,private_channel")` — list channels
- `slack_channel_info(channel)` — channel details (needs channel ID)
- `slack_channel_history(channel, limit=20)` — recent messages (user/text/ts)
- `slack_search_messages(query, count=10)` — search messages (user token required)
- `slack_list_users(limit=50)` — list workspace users
- `slack_user_info(user_id)` — user details
- `slack_add_reaction(channel, timestamp, emoji)` — add a reaction (emoji without colons)
- `slack_pin_message(channel, timestamp)` — pin a message
