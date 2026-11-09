---
name: deploy-package
description: Publicar o actualizar el paquete en npm. Se activa cuando el usuario quiere publicar o actualizar mcps-ai.
---

# Skill: Publicar en npm

## Pasos
1. Bump version en package.json (semver: patch/minor/major)
2. `npm pack --dry-run` → revisar archivos y tamaño
3. `npm publish` (requiere 2FA en app de autenticador)
   ```bash
   npm publish --otp=123456
   ```
4. `git tag v$(node -p "require('./package.json').version")`
5. `git push --tags`

## Requisitos
- Cuenta npm válida
- Token granular con Bypass 2FA (o 2FA activo + OTP)
- `npm whoami` debe funcionar

## Si falla con 403
- Token sin Bypass 2FA → crear nuevo Granular Access Token con Bypass 2FA
- `npm view mcps-ai` debe mostrar la última versión publicada
