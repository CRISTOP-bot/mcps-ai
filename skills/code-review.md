---
name: code-review
description: Revisar código eficientemente — preguntas clave, patrones, bugs comunes. Se activa cuando el usuario pide review de código.
---

# Skill: Code review

## Preguntas clave
1. ¿Hace lo que se supone que hace?
2. ¿Es legible? ¿Nombres descriptivos?
3. ¿Maneja errores?
4. ¿Hay duplicación?
5. ¿Tests?

## Bugs comunes en Python
- `except:` sin tipo → captura todo, malo
- `mutable default argument` → `def f(x=[])`
- `== None` → usar `is None`
- Paths hardcodeados → usar `os.path.join` o pathlib

## Bugs comunes en MCP
- No verificar `.env` antes de usar
- No truncar resultados enormes
- Raises en tools → usar `return {"error": ...}`
- No cerrar recursos (RCON, HTTP)

## Seguridad
- Secrets en código
- Paths sin validar
- SQL injection (si hay DB)
- Command injection (subprocess con shell=True)
