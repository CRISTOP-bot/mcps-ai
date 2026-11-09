---
name: caching-strategies
description: Estrategias de caché — in-memory, TTL, invalidación. Se activa cuando se optimiza lecturas repetidas.
---

# Skill: Caché

## Patrones
- **Cache-aside**: leer cache → miss → leer origen → guardar
- **TTL corto** para datos frescos (60s), largo para estáticos
- **Invalidación explícita** tras writes

## In-memory en Python
```python
_cache = {}
def cached(key, ttl, fn):
    hit = _cache.get(key)
    if hit and hit['exp'] > time.time(): return hit['value']
    value = fn(); _cache[key] = {'value': value, 'exp': time.time() + ttl}
    return value
```
