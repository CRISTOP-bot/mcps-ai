---
name: ai-memory
description: Gestionar contexto de conversación — qué recordar, qué olvidar, resumen. Se activa cuando la sesión es larga.
---

# Skill: Memoria del agente

## Qué recordar
- Preferencias del usuario (editor, lenguaje, OS)
- Paths importantes (~/mcp-servers, ~/.config/opencode)
- Proyecto activo (mcps-ai)
- Tareas pendientes

## Qué olvidar
- Secretos y tokens (nunca persistir)
- Contenido de archivos enormes (resumir)
- Errores ya resueltos

## Al inicio de sesión
1. `mcps-ai status` → estado general
2. Revisar `git log --oneline -5` → contexto reciente
3. `pgrep -af telegram_worker.py` → worker vivo?

## Durante la sesión
- Si el usuario repite una instrucción, verificar último estado con tools
- No asumir que algo sigue donde lo dejaste
