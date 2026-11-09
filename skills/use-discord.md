---
name: use-discord
description: Usar Discord — enviar/editar/borrar mensajes, reacciones, canales, miembros. Se activa cuando el usuario pide Discord.
---

# Skill: Usar Discord

## Herramientas (namespace `discord`)
- `discord_send_message(channel_id, content)` — hasta 2000 chars
- `discord_send_webhook(content)` — vía DISCORD_WEBHOOK_URL
- `discord_list_guilds()` / `discord_list_channels(guild_id)` / `discord_channel_info(channel_id)`
- `discord_read_messages(channel_id, limit)`
- `discord_edit_message` / `discord_delete_message` / `discord_add_reaction(channel_id, message_id, emoji)`
- `discord_create_channel(guild_id, name)` / `discord_list_members(guild_id, limit)`

## Reglas
1. El bot necesita Message Content Intent habilitada y permisos Send/Read/Manage.
2. No enviar a canales sin confirmación.
3. No hacer spam; respetar rate limits (429 → esperar Retry-After).
