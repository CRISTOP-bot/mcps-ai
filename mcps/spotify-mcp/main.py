"""Spotify MCP Server - Control Spotify playback and library via the Web API."""

import os
import json
import time
import base64
import urllib.request as urllib_request
import urllib.error as urllib_error
import urllib.parse as urllib_parse
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Spotify - opencode")

SPOTIFY_API_BASE = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

_token_cache = {"access_token": None, "expires_at": 0.0}


def _get_access_token():
    """Return a valid access token via the refresh token flow, or None if not configured."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        return None
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]
    try:
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        body = urllib_parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }).encode("utf-8")
        req = urllib_request.Request(
            SPOTIFY_TOKEN_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        with urllib_request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not token:
            return None
        _token_cache["access_token"] = token
        _token_cache["expires_at"] = now + expires_in - 60  # refresh 60s early
        return token
    except Exception:
        return None


def _not_configured():
    return {"error": "SPOTIFY_* not configured. Set SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET and SPOTIFY_REFRESH_TOKEN in the environment or .env file."}


def _api(method, path, body=None, params=None):
    """Make an authenticated Spotify Web API request. Returns (status_code, parsed_json_or_None)."""
    token = _get_access_token()
    if not token:
        return None, None
    url = SPOTIFY_API_BASE + path
    if params:
        qs = urllib_parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url += ("&" if "?" in url else "?") + qs
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif method in ("POST", "PUT"):
        data = b""
    req = urllib_request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib_request.urlopen(req, timeout=15) as r:
            raw = r.read()
            if r.status == 204 or not raw:
                return r.status, None
            return r.status, json.loads(raw.decode("utf-8", errors="replace"))
    except urllib_error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8", errors="replace"))
            msg = err_body.get("error", {})
            msg = msg.get("message") if isinstance(msg, dict) else str(msg)
            return e.code, {"error": msg or f"HTTP {e.code}"}
        except Exception:
            return e.code, {"error": f"HTTP {e.code}"}
    except Exception as e:
        return None, {"error": str(e)}


def _call(method, path, body=None, params=None):
    """Wrapper around _api with standard status handling."""
    token = _get_access_token()
    if not token:
        return _not_configured()
    status, payload = _api(method, path, body=body, params=params)
    if status is None and payload and "error" in payload:
        return payload
    if status == 204:
        return {"status": "ok"}
    if status and 200 <= status < 300:
        return payload if isinstance(payload, dict) else {"status": "ok", "data": payload}
    if isinstance(payload, dict):
        return payload
    return {"error": f"HTTP {status}"}


def _track_brief(track):
    if not track:
        return None
    artists = ", ".join(a.get("name", "") for a in track.get("artists", []))
    album = (track.get("album") or {}).get("name")
    return {
        "name": track.get("name"),
        "artist": artists,
        "album": album,
        "uri": track.get("uri"),
        "id": track.get("id"),
        "duration_ms": track.get("duration_ms"),
    }


@mcp.tool
async def spotify_search(query: str, search_type: str = "track", limit: int = 10):
    """Search Spotify for tracks, artists, albums or playlists. search_type: track|artist|album|playlist"""
    if search_type not in ("track", "artist", "album", "playlist"):
        return {"error": "search_type must be one of: track, artist, album, playlist"}
    try:
        limit = max(1, min(int(limit), 50))
        result = _call("GET", "/search", params={"q": query, "type": search_type, "limit": limit})
        if "error" in result:
            return result
        key = search_type + "s"
        items = (result.get(key) or {}).get("items", [])
        results = []
        for item in items:
            if search_type == "track":
                results.append(_track_brief(item))
            else:
                results.append({
                    "name": item.get("name"),
                    "uri": item.get("uri"),
                    "id": item.get("id"),
                    "type": search_type,
                })
        return {"query": query, "search_type": search_type, "count": len(results), "results": results}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_now_playing():
    """Get the currently playing track, artist, album and playback progress."""
    try:
        result = _call("GET", "/me/player")
        if "error" in result:
            return result
        if not result:
            return {"is_playing": False, "track": None}
        track = result.get("item") or {}
        brief = _track_brief(track) or {}
        return {
            "is_playing": result.get("is_playing"),
            "track": brief.get("name"),
            "artist": brief.get("artist"),
            "album": brief.get("album"),
            "uri": brief.get("uri"),
            "progress_ms": result.get("progress_ms"),
            "duration_ms": brief.get("duration_ms"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_play(context_uri: str = "", device_id: str = ""):
    """Start or resume playback. Optionally pass a context_uri (album/playlist/artist) and device_id."""
    try:
        body = {"context_uri": context_uri} if context_uri else None
        params = {"device_id": device_id} if device_id else None
        return _call("PUT", "/me/player/play", body=body, params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_pause(device_id: str = ""):
    """Pause playback, optionally on a specific device."""
    try:
        params = {"device_id": device_id} if device_id else None
        return _call("PUT", "/me/player/pause", params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_next(device_id: str = ""):
    """Skip to the next track, optionally on a specific device."""
    try:
        params = {"device_id": device_id} if device_id else None
        return _call("POST", "/me/player/next", params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_previous(device_id: str = ""):
    """Skip to the previous track, optionally on a specific device."""
    try:
        params = {"device_id": device_id} if device_id else None
        return _call("POST", "/me/player/previous", params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_set_volume(volume_percent: int, device_id: str = ""):
    """Set playback volume (0-100), optionally on a specific device."""
    try:
        volume_percent = max(0, min(int(volume_percent), 100))
        params = {"volume_percent": volume_percent}
        if device_id:
            params["device_id"] = device_id
        return _call("PUT", "/me/player/volume", params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_queue(track_uri: str, device_id: str = ""):
    """Add a track to the playback queue. track_uri like spotify:track:..."""
    try:
        params = {"uri": track_uri}
        if device_id:
            params["device_id"] = device_id
        return _call("POST", "/me/player/queue", params=params)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_list_playlists(limit: int = 20):
    """List the current user's playlists."""
    try:
        limit = max(1, min(int(limit), 50))
        result = _call("GET", "/me/playlists", params={"limit": limit})
        if "error" in result:
            return result
        playlists = []
        for item in result.get("items", []):
            playlists.append({
                "name": item.get("name"),
                "id": item.get("id"),
                "uri": item.get("uri"),
                "tracks": (item.get("tracks") or {}).get("total"),
                "public": item.get("public"),
                "owner": (item.get("owner") or {}).get("display_name"),
            })
        return {"count": len(playlists), "playlists": playlists}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_playlist_tracks(playlist_id: str, limit: int = 30):
    """List tracks in a playlist."""
    try:
        limit = max(1, min(int(limit), 100))
        result = _call("GET", f"/playlists/{urllib_parse.quote(playlist_id)}/tracks", params={"limit": limit})
        if "error" in result:
            return result
        tracks = []
        for item in result.get("items", []):
            brief = _track_brief(item.get("track"))
            if brief:
                tracks.append(brief)
        return {"playlist_id": playlist_id, "count": len(tracks), "tracks": tracks}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_create_playlist(name: str, description: str = "", public: bool = False):
    """Create a new playlist for the current user."""
    try:
        body = {"name": name, "description": description, "public": bool(public)}
        result = _call("POST", "/me/playlists", body=body)
        if "error" in result:
            return result
        return {
            "status": "ok",
            "name": result.get("name"),
            "id": result.get("id"),
            "uri": result.get("uri"),
            "url": (result.get("external_urls") or {}).get("spotify"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_list_devices():
    """List the user's available Spotify devices."""
    try:
        result = _call("GET", "/me/player/devices")
        if "error" in result:
            return result
        devices = []
        for d in result.get("devices", []):
            devices.append({
                "id": d.get("id"),
                "name": d.get("name"),
                "type": d.get("type"),
                "is_active": d.get("is_active"),
                "volume_percent": d.get("volume_percent"),
            })
        return {"count": len(devices), "devices": devices}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_saved_tracks(limit: int = 20):
    """List the user's saved (liked) tracks."""
    try:
        limit = max(1, min(int(limit), 50))
        result = _call("GET", "/me/tracks", params={"limit": limit})
        if "error" in result:
            return result
        tracks = []
        for item in result.get("items", []):
            brief = _track_brief(item.get("track"))
            if brief:
                brief["added_at"] = item.get("added_at")
                tracks.append(brief)
        return {"count": len(tracks), "tracks": tracks}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def spotify_transfer_playback(device_id: str, play: bool = False):
    """Transfer playback to a device. Optionally start playing on it."""
    try:
        body = {"device_ids": [device_id], "play": bool(play)}
        return _call("PUT", "/me/player", body=body)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
