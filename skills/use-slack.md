---
name: use-slack
description: Usar Slack — enviar mensajes/DMs, listar canales, historial, usuarios, reacciones, pins. Se activa cuando el usuario pide Slack.
---

# Skill: Usar Slack

## Herramientas (namespace `slack`)
- `slack_auth_test()` — verificar conexión y workspace
- `slack_send_message(channel, text)` / `slack_send_dm(user_id, text)`
- `slack_list_channels()` / `slack_channel_info(channel)` / `slack_channel_history(channel, limit)`
- `slack_search_messages(query, count)` — requiere search:read (token de usuario)
- `slack_list_users()` / `slack_user_info(user_id)`
- `slack_add_reaction(channel, timestamp, emoji)` — sin colones
- `slack_pin_message(channel, timestamp)`

## Reglas
1. Token xoxb-... Bot scopes: chat:write, channels:read, channels:history, im:write, reactions:write, pins:write, users:read.
2. Slack responde HTTP 200 con ok:false ante errores — revisar siempre el campo `error`.
3. No enviar DMs masivos; confirmar destinatarios.
