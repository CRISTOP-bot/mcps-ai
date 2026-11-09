---
name: config-management
description: Gestión de configuración — env vars vs archivos, precedencia. Se activa cuando se diseña config de una app.
---

# Skill: Config

## Precedencia típica
defaults → archivo (.env) → env vars → flags CLI

## Reglas
- Config sensible: env/.env (nunca en repo)
- Config no sensible: archivo versionado (YAML/TOML)
- Validar al arrancar; fallar rápido con mensaje claro
