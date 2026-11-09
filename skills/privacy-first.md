---
name: privacy-first
description: Diseñar y usar los MCPs respetando privacidad — mínimo acceso, sin telemetría, sin terceros. Se activa siempre.
---

# Skill: Privacy-first design

## Principios
1. Mínimo acceso — cada MCP solo pide lo necesario
2. Sin terceros — no se envían datos a servicios externos (opcional)
3. Local-first — todo corre en tu máquina
4. Cifrado en tránsito cuando hay red
5. Los datos del usuario no salen de la máquina sin permiso

## En la práctica
- Filesystem solo accede a `$HOME` y `/tmp`
- System MCP enmascara secrets en env_vars
- Telegram worker solo responde a usuarios autorizados
- Gmail token se guarda solo en disco local (600)
- Gists son privados

## Nunca
- Subir datos personales a APIs sin consentimiento
- Loggear contenido de correos/archivos
- Compartir tokens entre máquinas sin backup cifrado
