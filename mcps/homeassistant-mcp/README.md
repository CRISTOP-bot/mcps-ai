# homeassistant-mcp

MCP server for controlling and querying [Home Assistant](https://www.home-assistant.io/) via its REST API. Built with [FastMCP](https://github.com/jlowin/fastmcp).

## Setup

1. **Create a long-lived access token in Home Assistant**:
   - Open your Home Assistant UI.
   - Go to your **Profile** (click your user name in the sidebar) → **Security** tab → **Long-Lived Access Tokens**.
   - Click **Create Token**, give it a name (e.g. `opencode-mcp`), and copy the token. It is shown only once.

2. **Configure environment variables**:
   - Copy `.env.example` to `.env` and fill in the values:

   ```
   HA_URL=http://homeassistant.local:8123
   HA_TOKEN=your-long-lived-access-token
   ```

   - `HA_URL`: base URL of your Home Assistant instance (no trailing slash; it will be stripped anyway).
   - `HA_TOKEN`: the long-lived access token you created.

3. **Install dependencies**:

   ```
   uv sync
   ```

4. **Run** (stdio transport, e.g. for use from an MCP client):

   ```
   uv run python main.py
   ```

## Example tool calls

- List all light states:
  - `ha_get_states(domain="light")`
- Get one entity:
  - `ha_get_state(entity_id="light.kitchen")`
- Call `light.turn_on` with brightness:
  - `ha_call_service(domain="light", service="turn_on", entity_id="light.kitchen", data_json="{\"brightness_pct\": 80}")`
- Turn on / off / toggle helpers:
  - `ha_turn_on(entity_id="light.kitchen", data_json="{\"brightness_pct\": 50}")`
  - `ha_turn_off(entity_id="light.kitchen")`
  - `ha_toggle(entity_id="switch.coffee_maker")`
- List domains and services:
  - `ha_list_domains()`
  - `ha_list_services(domain="light")`
- History:
  - `ha_get_history(entity_id="sensor.temperature", hours=24)`
- Fire a custom event:
  - `ha_fire_event(event_type="my_event", data_json="{\"foo\": \"bar\"}")`

If `HA_URL` or `HA_TOKEN` is missing, every tool returns `{"error": "HA_URL/HA_TOKEN not set"}` instead of raising.
