---
name: mcp-architecture
description: Entender cómo funcionan los MCPs internamente — protocolo, stdio, JSON-RPC, tools/list, tools/call. Se activa cuando el usuario pregunta cómo funcionan o quiere crear uno.
---

# Skill: Arquitectura MCP (Model Context Protocol)

## Protocolo
- Transporte: stdio (stdin/stdout) o HTTP/SSE
- Formato: JSON-RPC 2.0
- Handshake: `initialize` → `notifications/initialized` → `tools/list` → `tools/call`

## Mensaje típico
```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":1,"result":{"tools":[...]}}
```

## Crear un MCP
```python
from fastmcp import FastMCP
mcp = FastMCP("MiMCP")

@mcp.tool()
async def mi_tool(param: str):
    """Descripción — esto es lo que el agente lee."""
    return {"result": param}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Ciclo de vida
1. Agent (OpenCode/Claude) lanza el proceso
2. Agent envía `initialize`
3. Server responde con capabilities (tools, resources, prompts)
4. Agent llama tools cuando el usuario lo necesita
5. Server responde con resultado

## FastMCP
- Toda función con `@mcp.tool()` se expone automáticamente
- Docstring = descripción para el agente
- Parámetros tipados = schema JSON automático
