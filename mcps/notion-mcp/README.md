# notion-mcp

MCP server for the Notion API. Exposes 11 tools to search, read, create and archive Notion pages/databases via an internal integration.

## Setup

1. Go to https://www.notion.so/my-integrations and create a new **internal integration**.
2. Copy the integration's secret (starts with `ntn_...` or `secret_...`).
3. **Share** every page/database you want the integration to access: open the page in Notion → **Share** → **Invite** → select your integration. Without this step the API returns `object_not_found`.
4. Create a `.env` file next to `main.py` with:

   ```
   NOTION_API_KEY=ntn_your_secret_here
   ```

   (See `.env.example`.)

## Run

```bash
uv sync
uv run python main.py
```

The server uses stdio transport.

## Tools

| Tool | Description |
| --- | --- |
| `notion_search` | Search pages and databases by query. |
| `notion_get_page` | Compact page view (id, title, url, archived, timestamps). |
| `notion_create_page` | Create a page under a page (`parent_type="page"`) or database (`parent_type="database"`, title property auto-detected). |
| `notion_archive_page` | Archive (soft-delete) a page. |
| `notion_get_database` | Database title, url and property names/types. |
| `notion_query_database` | Query a database; optional raw JSON `filter_json`. |
| `notion_list_block_children` | List child blocks with type and plain text. |
| `notion_append_text` | Append a paragraph block with text. |
| `notion_get_block` | Get a single block. |
| `notion_list_users` | List workspace users. |
| `notion_whoami` | Get the bot user (useful setup check). |
