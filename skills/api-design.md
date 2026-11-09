---
name: api-design
description: Diseño de APIs REST para MCPs — endpoints, status codes, formato. Se activa cuando se expone una API HTTP.
---

# Skill: API design

## Principios
- Recursos (nouns), no acciones (verbs)
- `/users` no `/getUsers`
- HTTP methods correctos (GET, POST, PUT, DELETE)
- Status codes: 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Server Error

## JSON response
```json
{"status": "ok", "data": {...}}
{"status": "error", "message": "..."}
```

## Versioning
- `/api/v1/...`
- No romper clientes existentes

## OpenCode
- API en `http://127.0.0.1:4096/api/info`
- OpenAPI en `/api/info`
