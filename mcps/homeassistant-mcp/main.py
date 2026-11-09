"""Home Assistant MCP Server - control and query Home Assistant via its REST API."""

import os
import json
import urllib.request as urllib_request
import urllib.parse as urllib_parse
import urllib.error as urllib_error
from datetime import datetime, timedelta, timezone
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Home Assistant - opencode")


def _ha_config():
    """Return (base_url, token) or (None, None) with error dict handled by caller."""
    url = os.getenv("HA_URL", "").strip().rstrip("/")
    token = os.getenv("HA_TOKEN", "").strip()
    if not url or not token:
        return None, None
    return url, token


def _request(method, path, body=None, params=None):
    """Perform an authenticated request to the HA REST API.

    Returns (data, error_dict). Exactly one of the two is not None.
    """
    url, token = _ha_config()
    if not url:
        return None, {"error": "HA_URL/HA_TOKEN not set"}
    full_url = f"{url}{path}"
    if params:
        full_url = f"{full_url}?{urllib_parse.urlencode(params)}"
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    try:
        req = urllib_request.Request(full_url, data=data, headers=headers, method=method)
        with urllib_request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")
            if not raw.strip():
                return {}, None
            try:
                return json.loads(raw), None
            except Exception:
                return {"raw": raw}, None
    except urllib_error.HTTPError as e:
        try:
            body_excerpt = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            body_excerpt = ""
        return None, {"error": f"HTTP {e.code}: {body_excerpt}"}
    except Exception as e:
        return None, {"error": str(e)}


def _parse_data_json(data_json):
    """Parse an optional raw JSON object string. Returns (obj, error_dict)."""
    if not data_json or not data_json.strip():
        return {}, None
    try:
        parsed = json.loads(data_json)
    except Exception as e:
        return None, {"error": f"Invalid data_json: {e}"}
    if not isinstance(parsed, dict):
        return None, {"error": "data_json must be a JSON object"}
    return parsed, None


def _domain_of(entity_id):
    return entity_id.split(".", 1)[0] if "." in entity_id else entity_id


@mcp.tool
async def ha_get_states(domain: str = ""):
    """Get all entity states, optionally filtered by domain (e.g. 'light'). Compact, capped at 100."""
    try:
        data, err = _request("GET", "/api/states")
        if err:
            return err
        if not isinstance(data, list):
            return {"error": "Unexpected response from /api/states"}
        domain = domain.strip()
        out = []
        for ent in data:
            try:
                entity_id = ent.get("entity_id", "")
                if domain and _domain_of(entity_id) != domain:
                    continue
                attrs = ent.get("attributes") or {}
                out.append({
                    "entity_id": entity_id,
                    "state": ent.get("state"),
                    "friendly_name": attrs.get("friendly_name"),
                    "last_changed": ent.get("last_changed"),
                })
                if len(out) >= 100:
                    break
            except Exception:
                continue
        return {"count": len(out), "states": out}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_get_state(entity_id: str):
    """Get the full state of one entity, including attributes (attribute payload capped at 4000 chars)."""
    try:
        data, err = _request("GET", f"/api/states/{urllib_parse.quote(entity_id, safe='')}")
        if err:
            return err
        if not isinstance(data, dict):
            return {"error": "Unexpected response from /api/states/<entity_id>"}
        try:
            attrs = data.get("attributes") or {}
            attrs_json = json.dumps(attrs, default=str)
            if len(attrs_json) > 4000:
                attrs = {"_truncated": True, "preview": attrs_json[:4000]}
        except Exception:
            attrs = {"_error": "could not serialize attributes"}
        return {
            "entity_id": data.get("entity_id", entity_id),
            "state": data.get("state"),
            "attributes": attrs,
            "last_changed": data.get("last_changed"),
            "last_updated": data.get("last_updated"),
            "context": data.get("context"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_list_entities(domain: str = ""):
    """List entity_ids only, sorted. Optional domain filter. Capped at 300."""
    try:
        data, err = _request("GET", "/api/states")
        if err:
            return err
        if not isinstance(data, list):
            return {"error": "Unexpected response from /api/states"}
        domain = domain.strip()
        ids = []
        for ent in data:
            try:
                entity_id = ent.get("entity_id", "")
                if not entity_id:
                    continue
                if domain and _domain_of(entity_id) != domain:
                    continue
                ids.append(entity_id)
            except Exception:
                continue
        ids = sorted(set(ids))[:300]
        return {"count": len(ids), "entities": ids}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_list_domains():
    """List unique domains from /api/states with counts, sorted by domain."""
    try:
        data, err = _request("GET", "/api/states")
        if err:
            return err
        if not isinstance(data, list):
            return {"error": "Unexpected response from /api/states"}
        counts = {}
        for ent in data:
            try:
                entity_id = ent.get("entity_id", "")
                if not entity_id:
                    continue
                d = _domain_of(entity_id)
                counts[d] = counts.get(d, 0) + 1
            except Exception:
                continue
        domains = [{"domain": d, "count": counts[d]} for d in sorted(counts)]
        return {"count": len(domains), "domains": domains}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_call_service(domain: str, service: str, entity_id: str = "", data_json: str = ""):
    """Call a Home Assistant service. Body = {'entity_id': ...} merged with optional JSON object in data_json."""
    try:
        extra, err = _parse_data_json(data_json)
        if err:
            return err
        body = dict(extra)
        if entity_id and entity_id.strip():
            body["entity_id"] = entity_id.strip()
        data, err = _request("POST", f"/api/services/{urllib_parse.quote(domain, safe='')}/{urllib_parse.quote(service, safe='')}", body=body)
        if err:
            return err
        changed = data if isinstance(data, list) else []
        return {
            "called": f"{domain}.{service}",
            "entity_id": body.get("entity_id"),
            "changed_states": len(changed),
            "result": changed,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_toggle(entity_id: str):
    """Toggle an entity via homeassistant.toggle."""
    try:
        return await ha_call_service("homeassistant", "toggle", entity_id)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_turn_on(entity_id: str, data_json: str = ""):
    """Turn an entity on. Domain is derived from the entity_id prefix (e.g. light.kitchen -> light.turn_on)."""
    try:
        domain = _domain_of(entity_id.strip())
        if not domain:
            return {"error": "entity_id is required"}
        return await ha_call_service(domain, "turn_on", entity_id, data_json)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_turn_off(entity_id: str, data_json: str = ""):
    """Turn an entity off. Domain is derived from the entity_id prefix (e.g. light.kitchen -> light.turn_off)."""
    try:
        domain = _domain_of(entity_id.strip())
        if not domain:
            return {"error": "entity_id is required"}
        return await ha_call_service(domain, "turn_off", entity_id, data_json)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_list_services(domain: str = ""):
    """List available services (compact names + count). Optional domain filter."""
    try:
        data, err = _request("GET", "/api/services")
        if err:
            return err
        if not isinstance(data, list):
            return {"error": "Unexpected response from /api/services"}
        domain = domain.strip()
        out = []
        for entry in data:
            try:
                d = entry.get("domain", "")
                if domain and d != domain:
                    continue
                services = entry.get("services") or {}
                out.append({
                    "domain": d,
                    "services": sorted(services.keys()) if isinstance(services, dict) else [],
                    "count": len(services) if isinstance(services, dict) else 0,
                })
            except Exception:
                continue
        total = sum(e["count"] for e in out)
        return {"domain_count": len(out), "service_count": total, "domains": out}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_get_history(entity_id: str, hours: float = 24):
    """Get state history for an entity over the last N hours. Compact [{state, last_changed}], capped at 200."""
    try:
        try:
            hours = float(hours)
        except Exception:
            return {"error": "hours must be a number"}
        start = datetime.now(timezone.utc) - timedelta(hours=hours)
        start_iso = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "filter_entity_id": entity_id,
            "minimal_response": "",
            "no_attributes": "",
        }
        path = f"/api/history/period/{start_iso}"
        data, err = _request("GET", path, params=params)
        if err:
            return err
        out = []
        if isinstance(data, list):
            for series in data:
                if not isinstance(series, list):
                    continue
                for item in series:
                    try:
                        out.append({
                            "state": item.get("state"),
                            "last_changed": item.get("last_changed") or item.get("last_updated"),
                        })
                        if len(out) >= 200:
                            break
                    except Exception:
                        continue
                if len(out) >= 200:
                    break
        return {"entity_id": entity_id, "hours": hours, "count": len(out), "history": out}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def ha_fire_event(event_type: str, data_json: str = ""):
    """Fire a custom event on the Home Assistant event bus. Body = parsed data_json (optional JSON object)."""
    try:
        body, err = _parse_data_json(data_json)
        if err:
            return err
        data, err = _request("POST", f"/api/events/{urllib_parse.quote(event_type, safe='')}", body=body)
        if err:
            return err
        return {"fired": event_type, "result": data}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
