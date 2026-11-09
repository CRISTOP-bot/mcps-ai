---
name: llm-cost-optimization
description: Optimizar costo de llamadas a LLMs. Se activa cuando el usuario pregunta por tokens/costos.
---

# Skill: Costo LLM

## Tácticas
1. Modelo correcto — no usar el más grande para clasificación simple
2. Prompts cortos — contexto solo necesario
3. Cache — reutilizar respuestas idénticas
4. Stream — mejor UX, quizá mismos tokens
5. Fallback a modelos free (como en telegram-mcp)
6. Medir — tokens in/out por modelo por día
