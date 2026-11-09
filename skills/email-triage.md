---
name: email-triage
description: Triage de Gmail — priorizar, responder, archivar. Se activa cuando el usuario pide revisar correos.
---

# Skill: Triage de email

## Flujo
1. `gmail_get_unread()` → lista
2. Priorizar: ¿remitente importante? ¿deadline?
3. Para cada uno: responder ahora (borrador), delegar, o archivar
4. Archivar/etiquetar al procesar

## Atajos de búsqueda
- `is:unread newer_than:1d`
- `from:jefe@empresa.com is:unread`
