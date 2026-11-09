---
name: release-process
description: Proceso de release — versionar, etiquetar, publicar. Se activa cuando se hace release.
---

# Skill: Proceso de release

## Semver
- MAJOR.MINOR.PATCH
- Major: breaking changes
- Minor: nuevas features compatibles
- Patch: bugfixes

## Pasos
1. `npm version patch|minor|major` (bumpea + commit + tag)
2. Verificar tests: `pytest`
3. Verificar CI en GitHub
4. `npm publish` (requiere login + 2FA/bypass)
5. `git push --follow-tags`
6. Verificar: `npm view mcps-ai versions`

## Si falla publish
- 403 → activar Bypass 2FA en token granular
- 404 → nombre ya existe o cuenta sin permisos
- Version ya existe → `npm version patch` otra vez

## Changelog
- Mantener README o CHANGELOG.md actualizado
- Resumir features nuevas + fixes
