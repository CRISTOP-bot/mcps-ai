---
name: ci-cd-github-actions
description: Diseñar pipelines CI/CD con GitHub Actions. Se activa cuando se configura CI/CD.
---

# Skill: CI/CD con GitHub Actions

## Estructura básica
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync && uv run pytest
```

## Buenas prácticas
- Matrix por versión de lenguaje
- Cache de deps (uv cache, node_modules)
- Un job = un propósito (lint, test, build)
- Secrets en Settings → Secrets, nunca en YAML
- Branch protection: PR + CI verde para merge
