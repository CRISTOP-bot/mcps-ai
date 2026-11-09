"""System MCP Server - System info, processes, network, etc."""

import os
import subprocess
import json
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("System - kiro")


def run_cmd(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


@mcp.tool
async def sys_info():
    """Get system information (OS, CPU, memory, hostname)."""
    try:
        info = {
            "hostname": os.uname().nodename,
            "os": run_cmd("uname -s"),
            "kernel": run_cmd("uname -r"),
            "arch": run_cmd("uname -m"),
            "uptime": run_cmd("uptime -p"),
        }
        # CPU info
        cpu_info = run_cmd("lscpu 2>/dev/null | grep -E 'Model name|CPU|Architecture' | head -5")
        info["cpu"] = cpu_info.split("\n") if cpu_info != f"Error: {e}" else ""
        # Memory
        mem = run_cmd("free -h")
        info["memory"] = mem
        return info
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_processes(filter_name: str = "", limit: int = 20):
    """List running processes, optionally filtered by name."""
    try:
        cmd = f"ps aux --sort=-%cpu"
        if filter_name:
            cmd += f" | grep -i '{filter_name}' | grep -v grep"
        cmd += f" | head -{limit + 1}"
        output = run_cmd(cmd)
        return {"processes": output}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_top(lines: int = 15):
    """Show top processes by CPU usage."""
    output = run_cmd(f"ps aux --sort=-%cpu | head -{lines + 1}")
    return {"processes": output}


@mcp.tool
async def sys_memory():
    """Show memory usage."""
    output = run_cmd("free -h")
    return {"memory": output}


@mcp.tool
async def sys_disk():
    """Show disk usage."""
    output = run_cmd("df -h")
    return {"disk": output}


@mcp.tool
async def sys_network():
    """Show network interfaces and IPs."""
    output = run_cmd("ip addr show 2>/dev/null | grep -E '^[0-9]|inet ' | head -20")
    return {"network": output}


@mcp.tool
async def sys_ports():
    """Show listening ports."""
    output = run_cmd("ss -tuln 2>/dev/null || netstat -tuln 2>/dev/null | head -20")
    return {"ports": output}


@mcp.tool
async def sys_kill_process(pid: int, signal: str = "TERM"):
    """Kill a process by PID. signal: TERM (default), KILL, INT, HUP."""
    try:
        sig = signal.upper()
        if sig not in ["TERM", "KILL", "INT", "HUP", "STOP", "CONT"]:
            return {"error": f"Invalid signal: {signal}"}
        import signal as sig_module
        sig_num = getattr(sig_module, f"SIG{sig}", None)
        if sig_num is None:
            return {"error": f"Unknown signal: {signal}"}
        os.kill(pid, sig_num)
        return {"status": f"Signal {sig} sent to PID {pid}"}
    except ProcessLookupError:
        return {"error": f"No process with PID {pid}"}
    except PermissionError:
        return {"error": f"Permission denied for PID {pid}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_env_vars(filter_name: str = ""):
    """Show environment variables, optionally filtered."""
    try:
        if filter_name:
            env_vars = {k: v for k, v in os.environ.items() if filter_name.lower() in k.lower()}
        else:
            env_vars = dict(os.environ)
        # Mask sensitive values
        masked = {}
        for k, v in env_vars.items():
            if any(s in k.lower() for s in ["token", "password", "secret", "key", "api"]):
                masked[k] = v[:4] + "****" if len(v) > 4 else "****"
            else:
                masked[k] = v
        return {"env_vars": masked}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_logs(log_path: str = "/var/log/syslog", lines: int = 50):
    """Read system logs."""
    try:
        output = run_cmd(f"tail -n {lines} {log_path} 2>&1")
        return {"log": output, "path": log_path}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_services():
    """List systemd services."""
    output = run_cmd("systemctl --user list-units --type=service --state=running --no-pager --no-legend 2>&1 | head -30")
    return {"services": output}


@mcp.tool
async def sys_battery():
    """Show battery status."""
    output = run_cmd("upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>&1 | grep -E 'state|percentage|time|capacity' | head -5")
    if output:
        return {"battery": output}
    # Fallback
    output = run_cmd("cat /sys/class/power_supply/BAT*/capacity 2>&1")
    return {"battery_capacity": output}


if __name__ == "__main__":
    mcp.run(transport="stdio")
