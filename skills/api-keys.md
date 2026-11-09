---
name: api-keys
description: Gestión segura de API keys y tokens. Se activa cuando se usa una API key o token.
---

# Skill: API keys

## Almacenamiento
- `.env` con permisos 600
- Variables de entorno para CI
- Nunca en código

## Rotación
- Cada 90 días
- Inmediatamente si se filtra
- Revocar tokens viejos

## Scopes mínimos
- Solo los permisos necesarios
- Read-only donde sea posible

## Si se filtra
1. Rotar inmediatamente
2. Verificar logs por uso no autorizado
3. Notificar a equipo
