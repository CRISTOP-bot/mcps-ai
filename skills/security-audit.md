---
name: security-audit
description: Auditar seguridad del repo/MCPs antes de publicar. Se activa antes de git push público o npm publish.
---

# Skill: Auditoría de seguridad

## Checklist antes de publicar
- [ ] `git grep -l "9267030799\|AAHSJYr99\|3fE6p-3LXrFJn\|testpass123\|ghp_"` → 0 resultados
- [ ] `git ls-files | grep -iE "\.env$|\.env\.|\.netrc|id_rsa|\.npmrc|credentials.json|token.json"` → 0 archivos
- [ ] `find . -name ".venv" -o -name "__pycache__"` → 0
- [ ] `grep -r "TU_TOKEN\|YOUR_TOKEN" .` → solo placeholders
- [ ] `.gitignore` incluye `.env`, `.venv`, `__pycache__`, `*.db`, `*.bak*`

## Scanners útiles
```bash
gitleaks detect --no-git
trufflehog filesystem .
```

## Reglas
1. Nunca publicar token real.
2. Si se filtra, rotar inmediatamente.
3. Revisar diff antes de `git push`: `git diff --staged`.
4. Usar `.env.example` con valores vacíos/placeholders.
