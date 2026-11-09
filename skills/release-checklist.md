---
name: release-checklist
description: Checklist completa de release antes de publicar. Se activa antes de cada release.
---

# Skill: Release checklist

- [ ] Tests verdes en CI
- [ ] Version bumped (semver)
- [ ] CHANGELOG/README actualizado
- [ ] `npm pack --dry-run` revisado
- [ ] Wiki/docs sincronizados
- [ ] Tag `vX.Y.Z`
- [ ] Post-release: `npm view <pkg> version`
