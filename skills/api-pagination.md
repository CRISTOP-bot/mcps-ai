---
name: api-pagination
description: Paginación en APIs — offset, cursor, límites. Se activa cuando se consume o diseña paginación.
---

# Skill: Paginación

## Offset
- Simple: ?page=N&per_page=M
- Problema: lento en offsets grandes

## Cursor
- ?cursor=abc123 (opaco)
- Estable ante inserciones — preferido en GitHub/Notion/Spotify/Slack

## En tu código
- Siempre limitar resultados (tope 100/200)
- Acumular pages con cursor hasta agotar o cap
