"""Filesystem MCP Server - Read, write, and manage files on the local machine."""

import os
import json
import glob
from pathlib import Path
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Filesystem - kiro")

# Whitelist of allowed directories (security)
ALLOWED_DIRS = [
    os.path.expanduser("~"),
    "/tmp",
    "/home",
]
ALLOWED_EXTENSIONS = None  # None = all extensions allowed


def is_path_allowed(path: str) -> tuple[bool, str]:
    path = os.path.realpath(os.path.expanduser(path))
    for allowed in ALLOWED_DIRS:
        if path.startswith(allowed):
            return True, path
    return False, path


@mcp.tool
async def fs_read_file(path: str, encoding: str = "utf-8"):
    """Read a file and return its content."""
    ok, full_path = is_path_allowed(path)
    if not ok:
        return {"error": f"Path not allowed: {path}"}
    try:
        with open(full_path, "r", encoding=encoding, errors="replace") as f:
            content = f.read()
        return {
            "path": full_path,
            "size": len(content),
            "content": content[:50000],  # Limit to 50KB
            "truncated": len(content) > 50000,
        }
    except FileNotFoundError:
        return {"error": f"File not found: {full_path}"}
    except IsADirectoryError:
        return {"error": f"Is a directory: {full_path}. Use fs_list_dir instead."}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_write_file(path: str, content: str, append: bool = False):
    """Write content to a file (or append). Creates parent directories if needed."""
    ok, full_path = is_path_allowed(path)
    if not ok:
        return {"error": f"Path not allowed: {path}"}
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        mode = "a" if append else "w"
        with open(full_path, mode, encoding="utf-8") as f:
            f.write(content)
        return {"status": "written" if not append else "appended", "path": full_path, "size": len(content)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_list_dir(path: str = ".", pattern: str = "*", show_hidden: bool = False):
    """List directory contents. pattern supports glob (*.py, **/*.txt, etc.)"""
    ok, full_path = is_path_allowed(path)
    if not ok:
        return {"error": f"Path not allowed: {path}"}
    try:
        if "**" in pattern:
            files = list(Path(full_path).rglob(pattern))
        else:
            files = list(Path(full_path).glob(pattern))

        entries = []
        for f in sorted(files, key=lambda x: (not x.is_dir(), x.name.lower())):
            if not show_hidden and f.name.startswith("."):
                continue
            try:
                stat = f.stat()
                entries.append({
                    "name": f.name,
                    "path": str(f),
                    "type": "dir" if f.is_dir() else "file",
                    "size": stat.st_size if f.is_file() else None,
                    "modified": stat.st_mtime,
                })
            except PermissionError:
                entries.append({"name": f.name, "path": str(f), "type": "unknown", "size": None})

        return {"path": full_path, "entries": entries, "count": len(entries)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_search_files(directory: str, pattern: str, max_results: int = 20):
    """Search for files matching a pattern (glob) in a directory tree."""
    ok, full_path = is_path_allowed(directory)
    if not ok:
        return {"error": f"Path not allowed: {directory}"}
    try:
        matches = list(Path(full_path).rglob(pattern))[:max_results]
        return {
            "pattern": pattern,
            "directory": full_path,
            "matches": [str(m) for m in matches],
            "count": len(matches),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_search_content(directory: str, query: str, file_pattern: str = "*.py", max_results: int = 20):
    """Search for text content in files (like grep)."""
    ok, full_path = is_path_allowed(directory)
    if not ok:
        return {"error": f"Path not allowed: {directory}"}
    try:
        matches = []
        for f in Path(full_path).rglob(file_pattern):
            if len(matches) >= max_results:
                break
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fp:
                    for i, line in enumerate(fp, 1):
                        if query.lower() in line.lower():
                            matches.append({
                                "file": str(f),
                                "line": i,
                                "content": line.rstrip()[:200],
                            })
                            if len(matches) >= max_results:
                                break
            except (PermissionError, IsADirectoryError):
                continue

        return {"query": query, "matches": matches, "count": len(matches)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_delete_file(path: str):
    """Delete a file or empty directory."""
    ok, full_path = is_path_allowed(path)
    if not ok:
        return {"error": f"Path not allowed: {path}"}
    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            return {"status": "deleted", "path": full_path}
        elif os.path.isdir(full_path):
            os.rmdir(full_path)
            return {"status": "deleted (empty dir)", "path": full_path}
        else:
            return {"error": f"Not found: {full_path}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_move_file(source: str, destination: str):
    """Move or rename a file."""
    ok_src, src = is_path_allowed(source)
    ok_dst, dst = is_path_allowed(destination)
    if not ok_src or not ok_dst:
        return {"error": f"Path not allowed"}
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
        return {"status": "moved", "from": src, "to": dst}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_file_info(path: str):
    """Get detailed info about a file or directory."""
    ok, full_path = is_path_allowed(path)
    if not ok:
        return {"error": f"Path not allowed: {path}"}
    try:
        stat = os.stat(full_path)
        import time
        return {
            "path": full_path,
            "name": os.path.basename(full_path),
            "type": "dir" if os.path.isdir(full_path) else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "permissions": oct(stat.st_mode & 0o777),
            "owner": stat.st_uid,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def fs_disk_usage(path: str = "."):
    """Get disk usage of a path."""
    try:
        usage = os.statvfs(path)
        return {
            "path": path,
            "total_bytes": usage.f_frsize * usage.f_blocks,
            "free_bytes": usage.f_frsize * usage.f_bavail,
            "used_bytes": usage.f_frsize * (usage.f_blocks - usage.f_bfree),
            "total_gb": round(usage.f_frsize * usage.f_blocks / (1024**3), 2),
            "free_gb": round(usage.f_frsize * usage.f_bavail / (1024**3), 2),
            "percent_used": round((usage.f_blocks - usage.f_bfree) / usage.f_blocks * 100, 1),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
