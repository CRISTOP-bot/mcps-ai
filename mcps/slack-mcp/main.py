"""Slack MCP Server - Interact with Slack via the Slack Web API."""

import os
import json
import urllib.request as urllib_request
import urllib.parse as urllib_parse
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Slack - opencode")

SLACK_API = "https://slack.com/api"


def _token():
    return os.environ.get("SLACK_BOT_TOKEN", "").strip()


def _request(method, params=None, post=False):
    """Call a Slack API method. GET-ish by default; post=True sends a JSON body."""
    token = _token()
    if not token:
        return {"error": "SLACK_BOT_TOKEN not set"}
    try:
        params = params or {}
        headers = {"Authorization": f"Bearer {token}"}
        if post:
            body = json.dumps(params).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
            req = urllib_request.Request(f"{SLACK_API}/{method}", data=body, headers=headers, method="POST")
        else:
            qs = urllib_parse.urlencode(params)
            url = f"{SLACK_API}/{method}" + (f"?{qs}" if qs else "")
            req = urllib_request.Request(url, headers=headers, method="GET")
        with urllib_request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        if not data.get("ok"):
            return {"error": data.get("error", "unknown_error")}
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_auth_test():
    """Who am I (team/user/bot_id). Useful for setup checks."""
    try:
        data = _request("auth.test")
        if "error" in data:
            return data
        return {"ok": True, "team": data.get("team"), "team_id": data.get("team_id"),
                "user": data.get("user"), "user_id": data.get("user_id"),
                "bot_id": data.get("bot_id"), "url": data.get("url")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_send_message(channel: str, text: str):
    """Send a message to a channel. channel = channel ID or #name."""
    try:
        data = _request("chat.postMessage", {"channel": channel, "text": text}, post=True)
        if "error" in data:
            return data
        return {"ok": True, "channel": data.get("channel"), "ts": data.get("ts"),
                "message": (data.get("message") or {}).get("text", text)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_send_dm(user_id: str, text: str):
    """Send a direct message to a user by user_id (opens a DM conversation first)."""
    try:
        conv = _request("conversations.open", {"users": user_id}, post=True)
        if "error" in conv:
            return conv
        channel = (conv.get("channel") or {}).get("id")
        if not channel:
            return {"error": "could not open DM conversation"}
        data = _request("chat.postMessage", {"channel": channel, "text": text}, post=True)
        if "error" in data:
            return data
        return {"ok": True, "channel": channel, "ts": data.get("ts")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_list_channels(limit: int = 50, channel_type: str = "public_channel,private_channel"):
    """List channels. channel_type is a comma-separated list (public_channel,private_channel,mpim,im)."""
    try:
        data = _request("conversations.list", {"limit": limit, "types": channel_type})
        if "error" in data:
            return data
        channels = [{"id": c.get("id"), "name": c.get("name"), "is_private": c.get("is_private"),
                     "is_member": c.get("is_member"), "num_members": c.get("num_members")}
                    for c in data.get("channels", [])]
        return {"channels": channels, "count": len(channels)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_channel_info(channel: str):
    """Get info about a channel. Requires channel ID."""
    try:
        data = _request("conversations.info", {"channel": channel})
        if "error" in data:
            return data
        c = data.get("channel", {})
        return {"id": c.get("id"), "name": c.get("name"), "is_private": c.get("is_private"),
                "is_archived": c.get("is_archived"), "is_member": c.get("is_member"),
                "num_members": c.get("num_members"), "topic": (c.get("topic") or {}).get("value"),
                "purpose": (c.get("purpose") or {}).get("value"), "created": c.get("created")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_channel_history(channel: str, limit: int = 20):
    """Get recent messages from a channel. Returns user/text/ts for each message."""
    try:
        data = _request("conversations.history", {"channel": channel, "limit": limit})
        if "error" in data:
            return data
        messages = [{"user": m.get("user"), "text": m.get("text"), "ts": m.get("ts")}
                    for m in data.get("messages", [])]
        return {"channel": channel, "messages": messages, "count": len(messages)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_search_messages(query: str, count: int = 10):
    """Search messages. Requires a user token with search:read scope; bot tokens usually fail with missing_scope."""
    try:
        data = _request("search.messages", {"query": query, "count": count})
        if "error" in data:
            return data
        matches = [{"user": (m.get("user") or {}).get("id") if isinstance(m.get("user"), dict) else m.get("user"),
                    "text": m.get("text"), "ts": m.get("ts"),
                    "channel": (m.get("channel") or {}).get("id")}
                   for m in ((data.get("messages") or {}).get("matches") or [])]
        return {"query": query, "matches": matches, "count": len(matches)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_list_users(limit: int = 50):
    """List users in the workspace."""
    try:
        data = _request("users.list", {"limit": limit})
        if "error" in data:
            return data
        users = [{"id": u.get("id"), "name": u.get("name"),
                  "real_name": (u.get("profile") or {}).get("real_name"),
                  "is_bot": u.get("is_bot"), "is_admin": u.get("is_admin"),
                  "deleted": u.get("deleted")}
                 for u in data.get("members", [])]
        return {"users": users, "count": len(users)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_user_info(user_id: str):
    """Get info about a user by user_id."""
    try:
        data = _request("users.info", {"user": user_id})
        if "error" in data:
            return data
        u = data.get("user", {})
        p = u.get("profile") or {}
        return {"id": u.get("id"), "name": u.get("name"), "real_name": p.get("real_name"),
                "display_name": p.get("display_name"), "email": p.get("email"),
                "title": p.get("title"), "is_bot": u.get("is_bot"),
                "is_admin": u.get("is_admin"), "tz": u.get("tz")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_add_reaction(channel: str, timestamp: str, emoji: str):
    """Add a reaction to a message. emoji WITHOUT colons (e.g. 'thumbsup')."""
    try:
        emoji = emoji.strip(":")
        data = _request("reactions.add", {"channel": channel, "timestamp": timestamp, "name": emoji}, post=True)
        if "error" in data:
            return data
        return {"ok": True, "channel": channel, "timestamp": timestamp, "emoji": emoji}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def slack_pin_message(channel: str, timestamp: str):
    """Pin a message in a channel by its timestamp."""
    try:
        data = _request("pins.add", {"channel": channel, "timestamp": timestamp}, post=True)
        if "error" in data:
            return data
        return {"ok": True, "channel": channel, "timestamp": timestamp}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
