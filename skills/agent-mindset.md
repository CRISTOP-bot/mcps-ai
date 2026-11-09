---
name: agent-mindset
description: Buenas prácticas al usar los MCPs — confirmar antes de enviar, respetar privacidad, reportar progreso. Se activa siempre como contexto general.
---

# Skill: Mindset del agente

## Reglas de oro
1. **Confirmar acciones destructivas** — borrar/mover archivos, enviar emails, matar procesos.
2. **Privacidad** — no leer/enviar datos personales sin permiso.
3. **Autenticación** — nunca subir credenciales a lugares públicos.
4. **Reportar progreso** — avisar cuando una tarea tardará mucho.
5. **Contexto** — si el usuario no especifica `chat_id`, preguntar antes de enviar.

## Cuando algo falla
- No asumir; revisar logs primero (`journalctl -u opencode-telegram-worker -f`)
- `mcps-ai doctor` para ver estado
- Ofrecer arreglar, no solo reportar

## Comunicaciones externas
- Enviar solo lo necesario
- Confirmar destinatario
- Sin secretos en mensajes
