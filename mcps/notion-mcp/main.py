"""Notion MCP Server - Interact with the Notion API via an internal integration."""

import os
import json
import urllib.request as urllib_request
import urllib.error as urllib_error
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Notion - opencode")

NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
MAX_TEXT = 20000


def notion_request(method, path, body=None):
    """Perform an authenticated Notion API request. Returns (data, error)."""
    key = os.environ.get("NOTION_API_KEY")
    if not key:
        return None, "NOTION_API_KEY not set"
    url = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib_request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib_request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")
            return (json.loads(raw) if raw else {}), None
    except urllib_error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
            parsed = json.loads(detail)
            msg = parsed.get("message", detail)
        except Exception:
            msg = str(e)
        return None, f"HTTP {e.code}: {msg}"
    except Exception as e:
        return None, str(e)


def trunc(text, limit=MAX_TEXT):
    if not isinstance(text, str):
        text = str(text)
    return text if len(text) <= limit else text[:limit] + "...[truncated]"


def extract_rich_text(obj):
    """Walk a dict/list and collect plain_text from any rich_text arrays."""
    parts = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "rich_text" and isinstance(v, list):
                    for rt in v:
                        if isinstance(rt, dict):
                            pt = rt.get("plain_text")
                            if pt:
                                parts.append(pt)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    try:
        walk(obj)
    except Exception:
        pass
    return "".join(parts)


def extract_title_from_page(page):
    """Extract the title from a page's properties (title or Name)."""
    try:
        props = page.get("properties", {}) or {}
        for prop in props.values():
            if isinstance(prop, dict) and prop.get("type") == "title":
                text = extract_rich_text(prop.get("title", []))
                if text:
                    return text
        # Fallback: any property with a title-like rich_text array
        for name, prop in props.items():
            if isinstance(prop, dict):
                text = extract_rich_text(prop)
                if text:
                    return text
    except Exception:
        pass
    return ""


def compact_page(page):
    return {
        "id": page.get("id"),
        "title": extract_title_from_page(page),
        "url": page.get("url"),
        "archived": page.get("archived"),
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
    }


def compact_block(block):
    btype = block.get("type", "unknown")
    text = extract_rich_text(block.get(btype, {})) if isinstance(block.get(btype), dict) else extract_rich_text(block)
    return {
        "id": block.get("id"),
        "type": btype,
        "text": trunc(text, 2000),
        "has_children": block.get("has_children"),
        "archived": block.get("archived"),
    }


@mcp.tool
async def notion_search(query: str, limit: int = 10):
    """Search Notion pages and databases by title/content."""
    try:
        limit = max(1, min(int(limit), 100))
        data, err = notion_request("POST", "/search", {"query": query, "page_size": limit})
        if err:
            return {"error": err}
        results = []
        for item in data.get("results", [])[:limit]:
            obj = item.get("object")
            entry = {
                "id": item.get("id"),
                "object": obj,
                "url": item.get("url"),
                "archived": item.get("archived"),
                "last_edited_time": item.get("last_edited_time"),
            }
            if obj == "page":
                entry["title"] = extract_title_from_page(item)
            elif obj == "database":
                entry["title"] = extract_rich_text(item.get("title", []))
            results.append(entry)
        return {"query": query, "count": len(results), "results": results}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_get_page(page_id: str):
    """Get a compact view of a Notion page (id, title, url, timestamps)."""
    try:
        data, err = notion_request("GET", f"/pages/{page_id}")
        if err:
            return {"error": err}
        return compact_page(data)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_create_page(parent_id: str, title: str, content: str = "", parent_type: str = "page"):
    """Create a Notion page under a page or database. parent_type: 'page' or 'database'."""
    try:
        if parent_type not in ("page", "database"):
            return {"error": "parent_type must be 'page' or 'database'"}

        title_prop_name = "title"
        if parent_type == "database":
            db, err = notion_request("GET", f"/databases/{parent_id}")
            if err:
                return {"error": f"Could not look up database to find title property: {err}"}
            try:
                for name, prop in (db.get("properties") or {}).items():
                    if isinstance(prop, dict) and prop.get("type") == "title":
                        title_prop_name = name
                        break
            except Exception:
                pass

        body = {
            "parent": {f"{parent_type}_id": parent_id},
            "properties": {
                title_prop_name: {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            },
        }
        if content:
            body["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": trunc(content, 1900)}}]
                    },
                }
            ]
        data, err = notion_request("POST", "/pages", body)
        if err:
            return {"error": err}
        return compact_page(data)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_archive_page(page_id: str):
    """Archive (soft-delete) a Notion page."""
    try:
        data, err = notion_request("PATCH", f"/pages/{page_id}", {"archived": True})
        if err:
            return {"error": err}
        return {"id": data.get("id"), "archived": data.get("archived"), "url": data.get("url")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_get_database(database_id: str):
    """Get a Notion database's title, url and property names."""
    try:
        data, err = notion_request("GET", f"/databases/{database_id}")
        if err:
            return {"error": err}
        props = {}
        try:
            for name, prop in (data.get("properties") or {}).items():
                props[name] = prop.get("type") if isinstance(prop, dict) else str(type(prop))
        except Exception:
            pass
        return {
            "id": data.get("id"),
            "title": extract_rich_text(data.get("title", [])),
            "url": data.get("url"),
            "properties": props,
            "archived": data.get("archived"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_query_database(database_id: str, limit: int = 20, filter_json: str = ""):
    """Query a Notion database. filter_json is an optional raw JSON filter string."""
    try:
        limit = max(1, min(int(limit), 100))
        body = {"page_size": limit}
        if filter_json and filter_json.strip():
            try:
                body["filter"] = json.loads(filter_json)
            except Exception as e:
                return {"error": f"Invalid filter_json: {e}"}
        data, err = notion_request("POST", f"/databases/{database_id}/query", body)
        if err:
            return {"error": err}
        results = [compact_page(item) for item in data.get("results", [])[:limit]]
        return {"database_id": database_id, "count": len(results), "has_more": data.get("has_more"), "results": results}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_list_block_children(block_id: str, limit: int = 30):
    """List child blocks of a block/page with type and plain text."""
    try:
        limit = max(1, min(int(limit), 100))
        data, err = notion_request("GET", f"/blocks/{block_id}/children?page_size={limit}")
        if err:
            return {"error": err}
        results = [compact_block(b) for b in data.get("results", [])[:limit]]
        total_text = trunc("\n".join(r["text"] for r in results if r.get("text")))
        return {"block_id": block_id, "count": len(results), "has_more": data.get("has_more"), "blocks": results, "text": total_text}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_append_text(block_id: str, text: str):
    """Append a paragraph block with the given text to a block/page."""
    try:
        body = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": trunc(text, 1900)}}]
                    },
                }
            ]
        }
        data, err = notion_request("PATCH", f"/blocks/{block_id}/children", body)
        if err:
            return {"error": err}
        results = [compact_block(b) for b in data.get("results", [])]
        return {"block_id": block_id, "appended": len(results), "blocks": results}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_get_block(block_id: str):
    """Get a single block (id, type, text, metadata)."""
    try:
        data, err = notion_request("GET", f"/blocks/{block_id}")
        if err:
            return {"error": err}
        return compact_block(data)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_list_users(limit: int = 50):
    """List users in the Notion workspace."""
    try:
        limit = max(1, min(int(limit), 100))
        data, err = notion_request("GET", f"/users?page_size={limit}")
        if err:
            return {"error": err}
        users = []
        for u in data.get("results", [])[:limit]:
            users.append({
                "id": u.get("id"),
                "type": u.get("type"),
                "name": u.get("name"),
                "avatar_url": u.get("avatar_url"),
                "email": (u.get("person") or {}).get("email") if isinstance(u.get("person"), dict) else None,
            })
        return {"count": len(users), "has_more": data.get("has_more"), "users": users}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def notion_whoami():
    """Get the bot user the integration is acting as (setup check)."""
    try:
        data, err = notion_request("GET", "/users/me")
        if err:
            return {"error": err}
        return {
            "id": data.get("id"),
            "type": data.get("type"),
            "name": data.get("name"),
            "avatar_url": data.get("avatar_url"),
            "bot": data.get("bot"),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
