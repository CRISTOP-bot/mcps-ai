---
name: oauth2-flows
description: Flujos OAuth2 — authorization code, refresh tokens, scopes. Se activa cuando se integra una API con OAuth2.
---

# Skill: OAuth2

## Authorization Code + Refresh Token (el de Spotify/Gmail)
1. Auth URL con client_id, redirect_uri, scope, state
2. Usuario autoriza → callback con ?code=
3. POST /token con code → access_token (1h) + refresh_token
4. Guardar refresh_token (nunca commitear)
5. Renovar: POST /token con grant_type=refresh_token

## Scopes mínimos
Pedir solo lo que necesitas; añadir scopes después si hace falta.

## Errores
- 401 → access_token expirado o inválido → refresh
- 400 invalid_grant → refresh token revocado → re-autenticar
