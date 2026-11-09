---
name: git-history-rewrite
description: Reescribir historial git — rebase -i, filter-branch, BFG. Se activa cuando hay commits sucios o secrets en el historial.
---

# Skill: Reescribir historial

## Interactive rebase
```bash
git rebase -i HEAD~10
# pick → reword/squash/drop/edit
```

## Borrar archivo sensible del historial
```bash
# Mejor: BFG
bfg --delete-files '*.env'
# o git filter-repo (preferido sobre filter-branch)
```
⚠️ Reescribir historial rompe clones compartidos — coordinar.
