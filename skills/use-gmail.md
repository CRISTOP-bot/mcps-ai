---
name: use-gmail
description: Usar Gmail API — leer, enviar, buscar, etiquetar y gestionar correos. Se activa cuando el usuario pide Gmail.
---

# Skill: Usar Gmail

## Herramientas disponibles (namespace `gmail`)
- `gmail_profile()` — perfil del usuario
- `gmail_list_emails(max_results, query, label)` — listar con búsqueda
- `gmail_get_unread()` / `gmail_unread_count()` — no leídos
- `gmail_read_email(email_id)` — leer correo completo (headers + body)
- `gmail_send_email(to, subject, body, cc, bcc, html)` — enviar
- `gmail_reply(email_id, body, reply_all)` — responder
- `gmail_forward(email_id, to, body)` — reenviar
- `gmail_search(query, max_results)` — buscar (sintaxis Gmail: from:, is:unread, etc.)
- `gmail_list_labels()`, `gmail_create_label(name)`, `gmail_add_label(email_id, label_id)`
- `gmail_mark_read / gmail_mark_unread` — marcar leído/no leído
- `gmail_archive(email_id)` / `gmail_delete_email(email_id)` — archivar/borrar
- `gmail_star(email_id)` / `gmail_unstar(email_id)` — destacar
- `gmail_get_thread(thread_id)` — ver conversación completa

## Reglas de uso
1. OAuth2 requerido — el usuario debe haber ejecutado `python gmail_auth.py` antes.
2. Nunca enviar emails sin confirmar con el usuario el destinatario y contenido.
3. Respetar privacidad: no leer emails personales sin autorización.
4. Consultar con `gmail_search("is:unread")` antes de "revisa mis correos".
5. Respetar límites de la API: no hacer miles de llamadas seguidas.
