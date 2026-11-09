---
name: multi-agent-setup
description: Configurar el mismo set de MCPs en múltiples agentes (OpenCode + Claude + Kiro + Cursor...). Se activa cuando el usuario usa varios editores/agentes.
---

# Skill: Multi-agent setup

## Config unificada
Cada agente usa un archivo diferente:
| Agente | Archivo | Formato raíz |
|--------|---------|--------------|
| OpenCode | `~/.config/opencode/opencode.json` | `mcp.servers` |
| Claude Desktop | `~/.config/claude/claude_desktop_config.json` | `mcpServers` |
| Claude Code | `.mcp.json` | `mcpServers` |
| Kiro | `~/.kiro/settings/mcp.json` | `mcpServers` |
| Cursor | `.cursor/mcp.json` | `mcpServers` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` |
| OpenClaw | `~/.openclaw/config.json` | `mcp.servers` |

## Estrategia
1. Instala con `npx mcps-ai install` → detecta todos los agentes
2. O copia manualmente el bloque `mcpServers` de un agente a otro
3. Las rutas absolutas deben ser las mismas en todos
4. Verifica con `mcps-ai status`

## Si tienes varios agentes
```bash
npx mcps-ai install    # detecta los 7
```
