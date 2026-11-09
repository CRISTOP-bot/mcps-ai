---
name: api-authentication-patterns
description: Patrones de autenticación en APIs — bearer, basic, HMAC, API keys. Se activa cuando se integra auth.
---

# Skill: Auth patterns

## Bearer token
`Authorization: Bearer <token>` — OAuth, PATs

## Basic
`Authorization: Basic base64(user:pass)` — registries, APIs simples

## HMAC signature
`X-Signature: sha256=...` — webhooks; verificar antes de procesar

## API key
`X-API-Key: ...` o query param — evitar query params si se puede

## Nunca
- Auth en query strings (quedan en logs)
- Tokens en mensajes/logs
