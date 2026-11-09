---
name: director-pattern
description: Patrón Director — dividir trabajo entre agentes especializados y sintetizar. Se activa cuando una tarea excede a un solo agente.
---

# Skill: Patrón Director

## Cuándo usarlo
- Tareas con partes independientes (investigar + implementar + revisar)
- Cuando quieres segundas opiniones críticas antes de decidir
- Síntesis de múltiples fuentes/roles

## Cómo funciona
1. **Fan-out**: cada worker recibe el objetivo + su rol, en paralelo
2. **Gather**: se recolectan los outputs (un fallo no tumba el run)
3. **Synthesize**: el Director recibe Goal + outputs y produce UNA respuesta accionable

## Buenas prácticas
- Roles complementarios, no redundantes
- Prompt del objetivo claro y único
- La respuesta del Director es la oficial; los workers son insumos
- Revisa el transcript si la síntesis no cuadras con lo esperado
