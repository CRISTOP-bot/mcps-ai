---
name: use-notion
description: Usar Notion — buscar, páginas, bases de datos, bloques, usuarios. Se activa cuando el usuario pide Notion.
---

# Skill: Usar Notion

## Herramientas (namespace `notion`)
- `notion_search(query, limit)` — buscar páginas/bases compartidas con la integración
- `notion_get_page(page_id)` / `notion_create_page(parent_id, title, content, parent_type)` / `notion_archive_page(page_id)`
- `notion_get_database(database_id)` / `notion_query_database(database_id, limit, filter_json)`
- `notion_list_block_children(block_id)` / `notion_append_text(block_id, text)` / `notion_get_block(block_id)`
- `notion_list_users()` / `notion_whoami()`

## Reglas
1. La integración solo ve páginas/bases compartidas vía "Invite integration" — si no encuentra algo, pedir compartir.
2. NOTION_API_KEY (ntn_...) + header Notion-Version 2022-06-28.
3. Para tareas: crear entrada en la base de datos con parent_type="database".
4. No archivar páginas sin confirmación.
