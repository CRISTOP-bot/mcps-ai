---
name: use-whatsapp
description: Usar WhatsApp — enviar/leer mensajes, buscar contactos, descargar media. Se activa cuando el usuario pide WhatsApp.
---

# Skill: Usar WhatsApp

## Herramientas disponibles (namespace `whatsapp`)
- `send_message(recipient, message)` — enviar mensaje de texto
- `send_file(recipient, media_path)` — enviar archivo/foto/audio
- `send_audio_message(recipient, media_path)` — audio como nota de voz
- `get_chat(chat_jid)` — metadatos de chat
- `get_last_interaction(jid)` — último mensaje del contacto
- `get_direct_chat_by_contact(sender_phone_number)` — buscar chat por número
- `search_contacts(query)` — buscar contactos por nombre o número
- `get_contact_chats(jid)` — chats con un contacto
- `download_media(message_id, chat_jid)` — descargar media
- `get_message_context(message_id, before, after)` — contexto de un mensaje

## Reglas
1. Usar JIDs correctos: `<número>@s.whatsapp.net` para contactos, `<id>@g.us` para grupos.
2. Para buscar contactos por nombre usar `search_contacts(query)`.
3. No enviar archivos sensibles a grupos.
4. Verificar que el bridge está conectado antes de enviar (mensajes han de tener `SendMessage` exitoso).
