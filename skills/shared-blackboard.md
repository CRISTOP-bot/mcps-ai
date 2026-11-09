---
name: shared-blackboard
description: Diseñar coordinación vía memoria compartida (blackboard) entre agentes. Se activa cuando agentes comparten estado.
---

# Skill: Blackboard compartida

## Qué guardar
- Hechos descubiertos (facts:api-rate-limit=5000)
- Decisiones intermedias (decision:storage=sqlite)
- Outputs de runs (run:<id> = JSON completo)

## Qué NO guardar
- Secretos (tokens) — la blackboard es texto plano
- Datos gigantes (cap 20k chars por tool)

## Patrón
```
worker A → blackboard_write("research:X", facts)
worker B → blackboard_read("research:X") → aplica
Director → blackboard_read("run:*") → sintetiza
```

## Limpieza
`orchestra_blackboard_delete(key)` para notas efímeras
