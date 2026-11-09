---
name: use-telegram
description: Usar Telegram desde el agente — leer/enviar mensajes, envío de archivos, búsqueda de chats. Se activa cuando el usuario pide enviar, leer, buscar o gestionar Telegram.
---

# Skill: Usar Telegram

## Herramientas disponibles (namespace `telegram`)
- `send_message(chat_id, text)` — enviar texto
- `send_photo / send_video / send_audio / send_voice / send_document` — enviar media y archivos
- `get_updates(offset, limit)` — obtener mensajes nuevos
- `get_chat(chat_id)` — info de un chat
- `get_chat_administrators / get_chat_member / get_chat_member_count` — miembros y admins
- `delete_message / edit_message_text / pin_chat_message / unpin_chat_message`
- `send_poll / stop_poll` — encuestas
- `set_my_commands / get_my_commands` — comandos del bot
- `ban_chat_member / unban_chat_member` — moderación

## Reglas de uso
1. Para enviar a un chat, usar `chat_id` numérico (ej: `8837193180`).
2. Validar que el chat existe con `get_chat` antes de enviar media.
3. Respetar privacidad: no enviar secretos a chats no autorizados.
4. Si el usuario pide "avisa por Telegram", usar el chat_id del usuario (preguntar si no lo sabes).
5. Respuestas del bot fuera de contexto: usar texto plano (sin markdown).

## Ejemplo
```
tools.telegram.send_message({ chat_id: "8837193180", text: "Listo ✅" })
```
