---
name: task-queue
description: Sistema de cola de tareas para agentes — orden, concurrencia, reintentos. Se activa cuando hay procesamiento en cola.
---

# Skill: Cola de tareas

## Diseño del worker
- Cola por chat_id (FIFO)
- Concurrencia máxima: 3
- Deduplicación por update_id
- Recuperación tras reinicio

## Algoritmo
```
while True:
  task = popleft()
  await process(task)
  mark_processed(task)
```

## Reglas
- Mensaje duplicado → ignorar (is_processed)
- Tarea fallida → marcar failed, no reintentar indefinidamente
- Tarea en progreso → status=running
- Timeout → marcar timeout
