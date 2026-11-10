"""System MCP Server - Cross-platform (Linux, macOS, Windows)."""

import os
import subprocess
import sys
import platform
import json
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("System - opencode")

IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform == "win32"


def run_cmd(cmd, timeout=10, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        return (result.stdout.strip() + ("\n" + result.stderr.strip() if result.stderr.strip() else "")).strip()
    except Exception as e:
        return f"Error: {e}"


@mcp.tool
async def sys_info():
    """Get system information (OS, CPU, memory, hostname)."""
    try:
        if IS_MACOS:
            cpu_brand = run_cmd("sysctl -n machdep.cpu.brand_string")
            ncpu = run_cmd("sysctl -n hw.ncpu")
            cpu_info = f"Model: {cpu_brand}\nCPUs: {ncpu}"
            mem = run_cmd("vm_stat")
            uptime = run_cmd("uptime")
        elif IS_LINUX:
            cpu_info = run_cmd("lscpu 2>/dev/null | grep -E 'Model name|^CPU\\(s\\)|Architecture' | head -5")
            mem = run_cmd("free -h")
            uptime = run_cmd("uptime")
        else:
            cpu_info = f"Processor: {platform.processor()}"
            mem = f"Memory: {os.popen('wmic OS get TotalVisibleMemorySize /value').read() if IS_WINDOWS else 'N/A'}"
            uptime = run_cmd("net statistics workstation 2>/dev/null | findstr /C:'Statistics started'")
        return {
            "hostname": os.uname().nodename,
            "os": platform.system(),
            "release": os.uname().release,
            "arch": platform.machine(),
            "uptime": uptime,
            "cpu": cpu_info.split("\n") if cpu_info else [],
            "memory": mem,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_processes(filter_name: str = "", limit: int = 20):
    """List running processes, optionally filtered by name."""
    try:
        limit = max(1, min(int(limit), 500))
        if IS_WINDOWS:
            cmd = ["tasklist"]
            if filter_name:
                cmd += ["/FI", f"IMAGENAME eq *{filter_name}*"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            lines = result.stdout.splitlines()
        else:
            args = ["ps", "aux"] if IS_MACOS else ["ps", "aux", "--sort=-%cpu"]
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            lines = result.stdout.splitlines()
            if filter_name:
                needle = filter_name.lower()
                header = lines[:1]
                lines = header + [l for l in lines[1:] if needle in l.lower()]
        return {"processes": "\n".join(lines[:limit + 1])}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_top(lines: int = 15):
    """Show top processes by CPU usage."""
    if IS_MACOS:
        output = run_cmd("ps aux | sort -rk 3,3 | head -" + str(lines + 1))
    elif IS_LINUX:
        output = run_cmd(f"ps aux --sort=-%cpu | head -{lines + 1}")
    else:
        output = run_cmd("tasklist")
    return {"processes": output}


@mcp.tool
async def sys_memory():
    """Show memory usage."""
    if IS_MACOS:
        output = run_cmd("vm_stat && echo '---' && top -l 1 -s 0 | grep PhysMem")
    elif IS_LINUX:
        output = run_cmd("free -h")
    else:
        output = run_cmd("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value")
    return {"memory": output}


@mcp.tool
async def sys_disk():
    """Show disk usage."""
    if IS_WINDOWS:
        output = run_cmd("wmic logicaldisk get size,freespace,caption")
    else:
        output = run_cmd("df -h")
    return {"disk": output}


@mcp.tool
async def sys_network():
    """Show network interfaces and IPs."""
    try:
        if IS_MACOS:
            output = run_cmd("ifconfig | grep -E '^[a-z]|inet ' | head -30")
        elif IS_LINUX:
            output = run_cmd("ip addr show 2>/dev/null | grep -E '^[0-9]|inet ' | head -20 || ifconfig | head -40")
        else:
            output = run_cmd("ipconfig")
        return {"network": output}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_ports():
    """Show listening ports."""
    try:
        if IS_MACOS:
            output = run_cmd("lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | head -20 || netstat -an -p tcp | grep LISTEN | head -20")
        elif IS_LINUX:
            output = run_cmd("ss -tuln 2>/dev/null | head -20 || netstat -tuln 2>/dev/null | head -20")
        else:
            output = run_cmd("netstat -an | findstr LISTENING")
        return {"ports": output}
    except Exception as e:
        return {"error": str(e)}


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
async def sys_logs(log_path: str = "", lines: int = 50):
    """Read the last N lines of a log file."""
    try:
        lines = max(1, min(int(lines), 2000))
        if not log_path:
            log_path = "/var/log/system.log" if IS_MACOS else "/var/log/syslog"
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                tail = f.readlines()[-lines:]
            return {"log": "".join(tail).rstrip(), "path": log_path}
        except PermissionError:
            return {"error": f"Permission denied: {log_path}", "path": log_path}
        except FileNotFoundError:
            return {"error": f"Log not found: {log_path}", "path": log_path}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_services():
    """List running system services."""
    if IS_MACOS:
        output = run_cmd("launchctl list | head -30")
    elif IS_LINUX:
        output = run_cmd("systemctl --user list-units --type=service --state=running --no-pager --no-legend 2>&1 | head -30")
    else:
        output = run_cmd("sc query state= running | head -50")
    return {"services": output}


@mcp.tool
async def sys_cpu():
    """Show CPU usage."""
    if IS_MACOS:
        output = run_cmd("top -l 1 -s 0 | grep -E 'CPU usage|PhysMem' | head -2")
    elif IS_LINUX:
        output = run_cmd("top -bn1 | head -5")
    else:
        output = run_cmd("wmic cpu get loadpercentage")
    return {"cpu": output}


@mcp.tool
async def sys_who():
    """Show logged-in users."""
    output = run_cmd("who" if not IS_WINDOWS else "query user")
    return {"users": output}


@mcp.tool
async def sys_uptime():
    """Show system uptime and load averages."""
    output = run_cmd("uptime")
    return {"uptime": output}


@mcp.tool
async def sys_kill_by_name(name: str, signal: str = "TERM"):
    """Kill all processes matching a name. signal: TERM, KILL, INT, HUP."""
    try:
        sig = signal.upper()
        if sig not in ["TERM", "KILL", "INT", "HUP", "STOP", "CONT"]:
            return {"error": f"Invalid signal: {signal}"}
        import signal as sig_module
        sig_num = getattr(sig_module, f"SIG{sig}", None)
        if sig_num is None:
            return {"error": f"Unknown signal: {signal}"}
        result = subprocess.run(["pkill", f"-{sig}", name], capture_output=True)
        return {"status": f"Signal {sig} sent to processes matching '{name}'", "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def sys_services_failed():
    """Show failed services."""
    if IS_MACOS:
        # No standard failed list; show unloaded running ones
        output = run_cmd("launchctl list | grep -v '^-' | grep -v PID | tail -20")
    elif IS_LINUX:
        output = run_cmd("systemctl --failed --no-pager --no-legend 2>&1 | head -20")
    else:
        output = run_cmd("sc query state= failed | head")
    return {"failed_services": output}


@mcp.tool
async def sys_temperature():
    """Show CPU/system temperature."""
    if IS_MACOS:
        output = run_cmd("sudo powermetrics --samplers smc -i1 -n1 2>&1 | grep -iE 'cpu|temp' | head -10 || echo 'Requires sudo; try: sudo powermetrics'")
    elif IS_LINUX:
        output = run_cmd("sensors 2>&1 | head -20 || cat /sys/class/thermal/thermal_zone*/temp 2>&1")
    else:
        output = run_cmd("wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature")
    return {"temperature": output}


@mcp.tool
async def sys_battery():
    """Show battery status."""
    if IS_MACOS:
        output = run_cmd("pmset -g batt")
    elif IS_LINUX:
        output = run_cmd("upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>&1 | grep -E 'state|percentage|time|capacity' | head -5 || cat /sys/class/power_supply/BAT*/capacity 2>&1")
    else:
        output = run_cmd("wmic path Win32_Battery get BatteryStatus,EstimatedChargeRemaining")
    return {"battery": output}


if __name__ == "__main__":
    mcp.run(transport="stdio")
