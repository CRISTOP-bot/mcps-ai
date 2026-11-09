---
name: incidents-runbook
description: Runbook de respuesta a incidentes — detección, mitigación, postmortem. Se activa cuando algo se rompió en producción.
---

# Skill: Runbook de incidentes

## Fases
1. **Triage** — qué falla, desde cuándo, alcance
2. **Mitigar** — rollback o workaround (fantasma primero, causa después)
3. **Comunicar** — estado claro a afectados
4. **Postmortem** — blameless, con timeline y acciones

## Preguntas clave
- ¿Qué cambió últimamente? (git log --since)
- ¿Logs: qué error es el primero cronológicamente?
- ¿Se puede revertir el último deploy?
