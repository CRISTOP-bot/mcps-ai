---
name: testing-strategy
description: Estrategia de testing para MCPs y workers. Se activa cuando se agregan tests al proyecto.
---

# Skill: Testing strategy

## Tipos de tests
1. **Unitarios** — funciones puras (session_store, task_manager)
2. **Integración** — MCP arranca y responde tools/list
3. **Mock** — RCON simulado, Telegram API simulada
4. **End-to-end** — flujo completo con bot real (manual)

## Qué testear en MCPs
- Tools responden con estructura correcta
- Errores se manejan graciosamente
- Tipos de input validados
- Conexiones se cierran

## Pytest + asyncio
```python
@pytest.mark.asyncio
async def test_task_manager():
    tm = TaskManager()
    ...
```

## CI
- Tests en cada push
- Import test: `python -c "import main"`
- 18 tests actualmente passing
