"""Discord MCP Server - Interact with Discord via the REST API (bot token or webhook)."""

import os
import json
import urllib.request as urllib_request
import urllib.error as urllib_error
import urllib.parse as urllib_parse
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Discord - opencode")

API_BASE = "https://discord.com/api/v10"


def _bot_token():
    return os.environ.get("DISCORD_BOT_TOKEN", "").strip()


def _webhook_url():
    return os.environ.get("DISCORD_WEBHOOK_URL", "").strip()


def _discord_request(method, path, body=None, token=None):
    """Make a Discord REST API request. Returns (status, parsed_json_or_None)."""
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib_request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bot {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "discord-mcp (https://github.com/mcps-ai)")
    try:
        with urllib_request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8", errors="replace")
            return r.status, (json.loads(raw) if raw else None)
    except urllib_error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else None
        except Exception:
            parsed = None
        return e.code, parsed if parsed is not None else {"message": raw or str(e)}


def _error_response(status, parsed):
    message = None
    if isinstance(parsed, dict):
        message = parsed.get("message")
    if not message:
        message = str(parsed) if parsed else "Unknown Discord API error"
    return {"error": f"Discord API error {status}: {message}", "status": status}


def _bot_request(method, path, body=None):
    """Bot-token request with auth check and error handling. Returns dict."""
    token = _bot_token()
    if not token:
        return {"error": "DISCORD_BOT_TOKEN not configured"}
    try:
        status, parsed = _discord_request(method, path, body, token)
        if status < 200 or status >= 300:
            return _error_response(status, parsed)
        return {"ok": True, "status": status, "data": parsed}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_send_message(channel_id: str, content: str):
    """Send a message to a Discord channel via the bot token. Content is truncated to 2000 characters."""
    try:
        result = _bot_request("POST", f"/channels/{channel_id}/messages", {"content": content[:2000]})
        if "error" in result:
            return result
        data = result.get("data") or {}
        return {"ok": True, "message_id": data.get("id"), "channel_id": channel_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_send_webhook(content: str, username: str = "mcps-ai"):
    """Send a message via the configured Discord webhook URL (DISCORD_WEBHOOK_URL)."""
    webhook = _webhook_url()
    if not webhook:
        return {"error": "DISCORD_WEBHOOK_URL not configured"}
    try:
        data = json.dumps({"content": content[:2000], "username": username}).encode("utf-8")
        req = urllib_request.Request(webhook, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "discord-mcp")
        try:
            with urllib_request.urlopen(req, timeout=15) as r:
                raw = r.read().decode("utf-8", errors="replace")
                parsed = json.loads(raw) if raw else None
                if r.status < 200 or r.status >= 300:
                    return _error_response(r.status, parsed)
                return {"ok": True, "status": r.status}
        except urllib_error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                parsed = None
            if parsed is None:
                parsed = {"message": raw or str(e)}
            return _error_response(e.code, parsed)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_list_guilds():
    """List the guilds (servers) the bot is a member of."""
    try:
        result = _bot_request("GET", "/users/@me/guilds")
        if "error" in result:
            return result
        guilds = [{"id": g.get("id"), "name": g.get("name")} for g in (result.get("data") or [])]
        return {"guilds": guilds, "count": len(guilds)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_list_channels(guild_id: str):
    """List text channels (type 0) in a guild with id, name and topic."""
    try:
        result = _bot_request("GET", f"/guilds/{guild_id}/channels")
        if "error" in result:
            return result
        channels = [
            {"id": c.get("id"), "name": c.get("name"), "topic": c.get("topic")}
            for c in (result.get("data") or [])
            if c.get("type") == 0
        ]
        return {"channels": channels, "count": len(channels)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_channel_info(channel_id: str):
    """Get information about a Discord channel."""
    try:
        result = _bot_request("GET", f"/channels/{channel_id}")
        if "error" in result:
            return result
        c = result.get("data") or {}
        return {
            "id": c.get("id"),
            "name": c.get("name"),
            "type": c.get("type"),
            "topic": c.get("topic"),
            "guild_id": c.get("guild_id"),
            "nsfw": c.get("nsfw"),
            "position": c.get("position"),
            "rate_limit_per_user": c.get("rate_limit_per_user"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_read_messages(channel_id: str, limit: int = 20):
    """Read recent messages from a channel (id, author, content, timestamp)."""
    try:
        limit = max(1, min(int(limit), 100))
        result = _bot_request("GET", f"/channels/{channel_id}/messages?limit={limit}")
        if "error" in result:
            return result
        messages = [
            {
                "id": m.get("id"),
                "author": (m.get("author") or {}).get("username"),
                "content": m.get("content"),
                "timestamp": m.get("timestamp"),
            }
            for m in (result.get("data") or [])
        ]
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_edit_message(channel_id: str, message_id: str, content: str):
    """Edit a message previously sent by the bot."""
    try:
        result = _bot_request(
            "PATCH",
            f"/channels/{channel_id}/messages/{message_id}",
            {"content": content[:2000]},
        )
        if "error" in result:
            return result
        data = result.get("data") or {}
        return {"ok": True, "message_id": data.get("id", message_id), "channel_id": channel_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_delete_message(channel_id: str, message_id: str):
    """Delete a message from a channel."""
    try:
        result = _bot_request("DELETE", f"/channels/{channel_id}/messages/{message_id}")
        if "error" in result:
            return result
        return {"ok": True, "message_id": message_id, "channel_id": channel_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_add_reaction(channel_id: str, message_id: str, emoji: str):
    """Add a reaction to a message. Emoji like '👍' is URL-encoded automatically."""
    try:
        token = _bot_token()
        if not token:
            return {"error": "DISCORD_BOT_TOKEN not configured"}
        encoded = urllib_parse.quote(emoji)
        result = _bot_request(
            "PUT",
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me",
        )
        if "error" in result:
            return result
        return {"ok": True, "message_id": message_id, "emoji": emoji}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_create_channel(guild_id: str, name: str, topic: str = ""):
    """Create a text channel (type 0) in a guild."""
    try:
        result = _bot_request(
            "POST",
            f"/guilds/{guild_id}/channels",
            {"name": name, "type": 0, "topic": topic},
        )
        if "error" in result:
            return result
        data = result.get("data") or {}
        return {"ok": True, "channel_id": data.get("id"), "name": data.get("name"), "guild_id": guild_id}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def discord_list_members(guild_id: str, limit: int = 20):
    """List members of a guild (requires Server Members Intent)."""
    try:
        limit = max(1, min(int(limit), 1000))
        result = _bot_request("GET", f"/guilds/{guild_id}/members?limit={limit}")
        if "error" in result:
            return result
        members = [
            {
                "id": (m.get("user") or {}).get("id"),
                "username": (m.get("user") or {}).get("username"),
                "nick": m.get("nick"),
                "roles": m.get("roles"),
                "joined_at": m.get("joined_at"),
            }
            for m in (result.get("data") or [])
        ]
        return {"members": members, "count": len(members)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == '__main__':
    mcp.run(transport="stdio")
