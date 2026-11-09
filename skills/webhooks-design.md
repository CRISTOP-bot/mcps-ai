---
name: webhooks-design
description: Diseñar webhooks seguros y confiables. Se activa cuando se recibe o envía webhooks.
---

# Skill: Webhooks

## Recibir
1. Verificar firma HMAC del payload
2. Responder 200 rápido; procesar async
3. Idempotencia: deduplicar por delivery ID

## Enviar
1. Reintentar con backoff ante 5xx
2. Timeout corto (5-10s)
3. No bloquear el emisor
