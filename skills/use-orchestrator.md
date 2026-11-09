---
name: use-orchestrator
description: Coordinar múltiples agentes IA con un Director — blackboard compartida, runs, mensajería. Se activa cuando el usuario pide varios agentes trabajando juntos.
---

# Skill: Usar Orchestrator MCP

## Flujo principal
```python
orchestra_director_run("tu objetivo", roles="researcher,coder,reviewer")
```
→ N workers creados como sesiones, corren EN PARALELO, el Director sintetiza una respuesta final.

## Agentes persistentes
- `orchestra_create_agent(name, role, system_prompt)` — agente con memoria de sesión
- `orchestra_send(agent_id, message)` — conversar con uno (bloquea, espera respuesta)
- `orchestra_broadcast(message, agent_ids="")` — mismo mensaje a varios en paralelo
- `orchestra_list_agents` / `orchestra_delete_agent`

## Coordinación
- `orchestra_blackboard_write(key, value)` / `_read` / `_list` — memoria compartida
- `orchestra_messages(limit, run_id)` — transcript de todo el equipo
- `orchestra_runs` — historial de director runs

## Personas worker
researcher, analyst, coder, reviewer, critic, planner, writer (+ genéricas).

## Reglas
1. Para objetivos grandes: `analyst,coder,reviewer` es buena combinación.
2. Revisa `orchestra_messages(run_id=...)` para ver qué dijo cada worker.
3. El Director manda: su síntesis es la respuesta final.
