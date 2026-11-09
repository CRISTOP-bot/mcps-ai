---
name: use-web
description: Búsqueda web y fetch de URLs — buscar en internet, leer páginas, noticias, clima. Se activa cuando el usuario pide "busca en internet" o quiere saber algo actual.
---

# Skill: Usar Web

## Herramientas disponibles (namespace `web`)
- `web_search(query, max_results)` — buscar en Bing (sin API key)
- `web_fetch(url, max_chars)` — descargar contenido de URL (extrae texto sin HTML)
- `web_news(query, max_results)` — buscar noticias
- `web_weather(city)` — clima para una ciudad (sin API key)

## Reglas
1. Preferir `web_fetch` para leer una página específica; usar `web_search` primero para encontrar URLs.
2. Muchos sitios bloquean bots — si `web_fetch` falla con 403/cloudflare, probar con `playwright`.
3. No hacer scraping agresivo (no miles de requests).
4. `web_weather` funciona para ciudades en cualquier idioma.
