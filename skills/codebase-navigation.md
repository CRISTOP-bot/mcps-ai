---
name: codebase-navigation
description: Navegar codebases grandes eficientemente. Se activa cuando el usuario pide explorar un repo desconocido.
---

# Skill: Navegar codebases

## Estrategia
1. README + estructura top-level (ls, tree -L 2)
2. Entry points (main, index, app)
3. Configuración (package.json, pyproject, Makefile)
4. Tests → entender comportamiento esperado
5. Grep por el símbolo relevante

## Red flags
- ¿Monorepo? Buscar workspaces en package.json
- ¿Generated code? No leer, excluir
