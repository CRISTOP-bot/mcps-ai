---
name: json-schema-mastery
description: Dominar JSON Schema — tipos, required, validación. Se activa cuando se valida JSON o se documenta APIs.
---

# Skill: JSON Schema

## Esenciales
```json
{
  "type": "object",
  "properties": { "name": { "type": "string", "minLength": 1 } },
  "required": ["name"]
}
```

- type: string|number|integer|boolean|object|array|null
- enum para valores fijos; pattern para regex
- additionalProperties:false para estrictos
