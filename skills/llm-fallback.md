---
name: llm-fallback
description: Arquitectura de fallback de modelos LLM cuando uno se queda sin tokens. Se activa cuando se diseña resiliencia.
---

# Skill: LLM fallback

## Estrategia del worker
```python
for model in AI_FALLBACK_MODELS:
    try:
        response = await full_request(session, text, model=model)
        if "limit" not in str(response).lower():
            return response
    except Exception:
        continue
```

## Modelos de fallback
1. deepseek-v4.1-flash-free
2. glm-5.3-flash-free
3. iceman-free
4. inkling-2-small-free
5. crouton-alpha-free
6. flint-40b-free
7. nemotron-3.5-super-vl-free
8. beam-free
9. mimo-v2.6-flash-free
10. nemotron-3.5-lightning-free
11. big-pickle

## Detección de límite
- "limit" in response
- "429" in response
- "free usage" in response

## Recuperación
- Guardar sesión
- Reintentar con siguiente modelo
- Si todos fallan, reportar al usuario
