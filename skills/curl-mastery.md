---
name: curl-mastery
description: cURL para APIs — headers, auth, JSON, retries. Se activa cuando se prueba una API por terminal.
---

# Skill: cURL

## Recetas
```bash
# GET con token
curl -s -H "Authorization: Bearer $TOKEN" https://api/x

# POST JSON
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"a":1}' https://api/x

# Ver solo status
curl -s -o /dev/null -w "%{http_code}\n" URL

# Seguir redirects
curl -sL URL
```
