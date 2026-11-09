---
name: dependencies
description: Gestión de dependencias Python — uv, pip, virtualenvs. Se activa al instalar o actualizar deps.
---

# Skill: Dependencias Python

## uv (recomendado)
```bash
uv venv
uv sync
uv run python script.py
uv add fastmcp
uv remove fastmcp
```

## pyproject.toml
```toml
[project]
dependencies = [
    "fastmcp>=3.4.4",
    "python-dotenv>=1.0.0",
]
```

## pip (alternativo)
```bash
pip install -r requirements.txt
```

## Versiones
- Pin major mínima: `fastmcp>=3.4.4`
- Evitar pin exacto: facilita updates
- `uv.lock` versiona todo (commit)

## Actualizar
```bash
uv lock --upgrade
uv sync
```
