---
name: api-rate-limits
description: Manejo de rate limits en APIs externas. Se activa cuando una API devuelve 429.
---

# Skill: Rate limits

## Estrategia
1. Respetar `Retry-After` header
2. Backoff exponencial con jitter: 1s, 2s, 4s, 8s...
3. Cachear respuestas cuando sea posible
4. Token bucket para limitar client-side

## Por proveedor
| API | Límite |
|-----|--------|
| GitHub | 5000 req/h (auth) |
| Notion | 3 req/s |
| Spotify | ~30 req/s |
| Slack | 1 req/s por método |
| Discord | por bucket, ver headers |
