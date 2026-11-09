---
name: git-commit-messages
description: Convenciones para mensajes de commit claros y semánticos. Se activa cuando el usuario pide hacer commit.
---

# Skill: Mensajes de commit

## Formato
```
<type>(<scope>): <subject>

<body>
```

## Types
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: documentación
- `style`: formato, sin cambio de lógica
- `refactor`: refactor sin cambiar comportamiento
- `test`: tests
- `chore`: mantenimiento, deps, build

## Ejemplos
```
feat(telegram): auto-switch model on token limit
fix(gmail): preserve token on CLI upgrade
docs(readme): add npx install instructions
```

## Reglas
- Imperativo: "Add feature" no "Added feature"
- Subject ≤ 72 chars
- Body explica el "qué y por qué", no el "cómo"
