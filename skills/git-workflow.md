---
name: git-workflow
description: Flujo de Git del proyecto — branches, commits, PRs. Se activa cuando se trabaja con git en mcps-ai.
---

# Skill: Flujo Git

## Branches
```
main → estable, solo merges de PRs aprobados + CI verde
```

## Comandos útiles
```bash
git status
git diff                    # cambios sin commit
git diff --staged           # cambios staged
git log --oneline -10       # últimos 10 commits
git add -p                  # stagear interactivamente
git commit -m "mensaje"
git push origin main
```

## Commits
- Imperativo: "Add X" / "Fix Y" / "Update Z"
- Cortos (máx 72 chars) + body descriptivo
- Un cambio lógico por commit

## CI
- GitHub Actions corre tests en cada push/PR
- Si falla: revisar logs en Actions tab
- Verde = mergeable

## Tags y releases
```bash
git tag v1.1.0
git push --tags
```
