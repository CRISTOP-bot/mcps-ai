---
name: agent-config-formats
description: Diferencias entre los formatos de config de cada agente. Se activa cuando el usuario configura un agente o migra entre agentes.
---

# Skill: Formatos de config de agentes

## OpenCode (~/.config/opencode/opencode.json)
```json
{
  "mcp": {
    "servers": {
      "telegram": { "type": "local", "command": [...], "environment": {...} }
    }
  }
}
```

## Claude Desktop (claude_desktop_config.json)
```json
{
  "mcpServers": {
    "telegram": { "command": "uv", "args": [...] }
  }
}
```

## Kiro (~/.kiro/settings/mcp.json)
```json
{
  "mcpServers": {
    "telegram": { "command": "uv", "args": [...], "environment": {...} }
  }
}
```

## Cursor / Claude Code / Windsurf / OpenClaw
Mismo formato que Claude Desktop: `mcpServers`.
OpenClaw usa `mcp.servers`.

## Convertir entre formatos
Es mecánico: renombrar raíz (`mcpServers` ↔ `mcp.servers`) y mantener tools.
