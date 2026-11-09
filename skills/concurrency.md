---
name: concurrency
description: Concurrencia async en Python/Node — asyncio, semaphores, locks. Se activa cuando se escribe código async.
---

# Skill: Concurrencia

## asyncio
```python
async def worker(sem):
    async with sem:
        await long_operation()

sem = asyncio.Semaphore(3)
```

## Locks
```python
lock = asyncio.Lock()
async with lock:
    shared_resource.update()
```

## Task management
```python
tasks = [asyncio.create_task(f(x)) for x in items]
await asyncio.gather(*tasks)
```

## Reglas
- No bloquear el event loop
- Semáforos para concurrencia máxima
- Locks para estado compartido
