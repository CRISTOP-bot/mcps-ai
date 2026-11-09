---
name: backup-credentials
description: Respaldar o restaurar credenciales de los MCPs (tokens, .env) en un Gist privado de GitHub. Se activa cuando el usuario quiere backup o restore.
---

# Skill: Backup/Restore de credenciales

## Flujo automático
```bash
mcps-ai login          # auth con GitHub (usa gh CLI o token)
mcps-ai backup         # sube .env etc a Gist privado
mcps-ai restore        # baja desde Gist y restaura con .bak
```

## Qué se respalda
- Todos los `.env` de los MCPs
- `credentials.json` / `token.json`
- `opencode.json`, `.kiro/settings/mcp.json`

## Reglas
1. El Gist es **privado** (`public: false`) — nunca público.
2. El token GitHub se guarda en `~/.mcps-ai/github-token` con permisos 600.
3. En `restore` se crean `.bak` antes de sobrescribir.
4. Si `gh` CLI está logueado, se usa automáticamente (`gh auth token`).
5. Si no, crear Personal Access Token en github.com/settings/tokens (scopes: gist, read:user, repo).
