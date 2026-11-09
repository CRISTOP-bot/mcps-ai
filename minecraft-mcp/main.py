"""Minecraft MCP Server - Control a Minecraft server via RCON."""

import os
import json
from fastmcp import FastMCP
from dotenv import load_dotenv
from rcon import RCONClient

load_dotenv()

mcp = FastMCP("Minecraft")

MC_HOST = os.getenv("MC_HOST", "localhost")
MC_PORT = int(os.getenv("MC_PORT", "25575"))
MC_PASSWORD = os.getenv("MC_RCON_PASSWORD", "")
MC_PLAYER = os.getenv("MC_PLAYER", "")

_rcon = None


def get_rcon():
    global _rcon
    if _rcon is None:
        _rcon = RCONClient(MC_HOST, MC_PORT, MC_PASSWORD)
        _rcon.connect()
    return _rcon


def mc_cmd(cmd):
    """Execute a Minecraft command via RCON."""
    rcon = get_rcon()
    try:
        return rcon.command(cmd)
    except Exception as e:
        # Reconnect
        global _rcon
        _rcon = None
        rcon = get_rcon()
        return rcon.command(cmd)


@mcp.tool
async def mc_status():
    """Get Minecraft server status (player count, TPS, etc)."""
    try:
        result = mc_cmd("list")
        return {"status": "ok", "players": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool
async def mc_players():
    """List online players."""
    try:
        return {"players": mc_cmd("list")}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_say(message: str):
    """Send a chat message to all players on the server."""
    try:
        result = mc_cmd(f"say {message}")
        return {"result": result or "Message sent"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_give(player: str, item: str, count: int = 1):
    """Give an item to a player. Item format: minecraft:diamond, minecraft:golden_apple, etc."""
    try:
        result = mc_cmd(f"give {player} {item} {count}")
        return {"result": result or f"Gave {count}x {item} to {player}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_tp(player: str, x: float, y: float, z: float):
    """Teleport a player to coordinates."""
    try:
        result = mc_cmd(f"tp {player} {x} {y} {z}")
        return {"result": result or f"Teleported {player} to {x}, {y}, {z}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_weather(weather_type: str):
    """Set weather. Options: clear, rain, thunder."""
    try:
        result = mc_cmd(f"weather {weather_type}")
        return {"result": result or f"Weather set to {weather_type}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_time(time_value: str):
    """Set time. Options: day, night, noon, midnight, or a number (0-24000)."""
    try:
        result = mc_cmd(f"time set {time_value}")
        return {"result": result or f"Time set to {time_value}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_gamemode(player: str, mode: str):
    """Set gamemode for a player. Modes: survival, creative, adventure, spectator."""
    try:
        result = mc_cmd(f"gamemode {mode} {player}")
        return {"result": result or f"Set {player} to {mode}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_command(command: str):
    """Execute any raw Minecraft server command."""
    try:
        result = mc_cmd(command)
        return {"result": result or "Command executed"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_locate(structure: str):
    """Locate a structure. Examples: village, temple, monument, mansion, fortress, stronghold, mineshaft."""
    try:
        result = mc_cmd(f"locate structure minecraft:{structure}")
        return {"result": result or f"Searching for {structure}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_summon(entity: str, x: float = None, y: float = None, z: float = None):
    """Summon an entity. If no coordinates, spawns at caller's location."""
    try:
        if x is not None and y is not None and z is not None:
            cmd = f"summon {entity} {x} {y} {z}"
        else:
            cmd = f"summon {entity}"
        result = mc_cmd(cmd)
        return {"result": result or f"Summoned {entity}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_effect(player: str, effect: str, duration: int = 30, amplifier: int = 0):
    """Give a potion effect to a player. Effect: speed, strength, jump_boost, etc."""
    try:
        result = mc_cmd(f"effect give {player} {effect} {duration} {amplifier}")
        return {"result": result or f"Gave {effect} to {player}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def mc_difficulty(difficulty: str):
    """Set difficulty. Options: peaceful, easy, normal, hard."""
    try:
        result = mc_cmd(f"difficulty {difficulty}")
        return {"result": result or f"Difficulty set to {difficulty}"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
