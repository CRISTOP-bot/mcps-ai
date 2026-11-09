---
name: code-quality-gates
description: Puertas de calidad en CI — lint, tipos, tests, cobertura. Se activa cuando se configura un quality gate.
---

# Skill: Quality gates

## Gates típicos
1. **Lint** — ruff (Python), eslint (JS)
2. **Types** — mypy --strict, tsc --noEmit
3. **Tests** — pytest, jest
4. **Coverage** — umbral mínimo (80%)
5. **Security** — gitleaks, pip-audit, npm audit

## Ejemplo CI job
```yaml
- run: uv run ruff check . && uv run mypy . && uv run pytest --cov
```
