---
name: secrets-rotation
description: Rotación periódica de secretos — tokens, keys, passwords. Se activa cuando se programa mantenimiento de seguridad.
---

# Skill: Rotación de secretos

## Calendario sugerido
- npm/tokens personales: 90 días o ante filtración
- OAuth credentials: anual
- Bot tokens: cuando cambien permisos

## Pasos
1. Crear nuevo secreto en paralelo
2. Desplegar/actualizar .env
3. Verificar funcionamiento
4. Revocar el viejo
5. Actualizar backup (mcps-ai backup)
