---
name: upgrades
description: Actualizar dependencias sin romper nada — estrategia de upgrade seguro. Se activa cuando se actualiza una dep.
---

# Skill: Upgrades seguros

## Estrategia
1. Backup del lock file (`cp uv.lock uv.lock.bak`)
2. Actualizar una dep a la vez
3. Correr tests
4. Si fallan, rollback

## Comandos
```bash
uv lock --upgrade-package fastmcp
uv sync
uv run pytest
```

## Verificar cambios
- `git diff uv.lock`
- Revisar breaking changes en changelog
- Probar flujo end-to-end
