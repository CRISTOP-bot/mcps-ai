---
name: error-handling
description: Manejo de errores robusto en MCPs y workers. Se activa cuando algo falla.
---

# Skill: Error handling

## Patrón en MCPs
```python
@mcp.tool()
async def my_tool(param: str):
    try:
        # operación
        return {"result": ...}
    except Exception as e:
        return {"error": str(e)}
```
NUNCA raise → el agente no puede manejar excepciones.

## Patrón en worker
```python
try:
    response = await self.ai.full_request(...)
except Exception as e:
    await self.send_telegram(chat_id, f"❌ {e}")
    store.mark_failed(...)
```

## Categorías de error
- **Externo** (API, red) → retry con backoff
- **Usuario** (input inválido) → mensaje claro
- **Interno** (bug) → log + alerta

## Timeouts
- OpenCode request → REQUEST_TIMEOUT=0 (tareas largas)
- HTTP → 10s
- MCP startup → 30s
