---
name: use-browser
description: Control de navegador Chrome/Chromium — navegar, clickear, llenar formularios, screenshots. Se activa cuando el usuario pide controlar un navegador o automatizar una web.
---

# Skill: Usar Browser

## Herramientas disponibles (namespace `browser`)
- `browser_navigate(url)` — ir a una URL
- `browser_click(selector)` — click en elemento (CSS selector)
- `browser_fill(selector, text)` — llenar input
- `browser_type(selector, text, delay)` — escribir con delay humano
- `browser_press(key)` — presionar tecla (Enter, Tab, Escape...)
- `browser_get_text(selector)` — obtener texto de un elemento (default: toda la página)
- `browser_get_html(selector)` — obtener HTML interno
- `browser_screenshot(full_page)` — captura en base64
- `browser_evaluate(script)` — ejecutar JavaScript y devolver resultado
- `browser_wait(selector, timeout)` — esperar a que aparezca elemento
- `browser_select(selector, option)` — seleccionar en <select>
- `browser_scroll(direction, amount)` — scroll
- `browser_back()` / `browser_forward()` / `browser_reload()`
- `browser_get_links()` — extraer todos los enlaces
- `browser_close()` — cerrar navegador

## Reglas
1. CSS selectors para elementos (ej: `#login`, `.btn-primary`, `input[name="query"]`).
2. Para páginas dinámicas, usar `browser_wait` en vez de asumir carga.
3. `screenshot` devuelve base64 — el agente puede mostrarla si el cliente lo soporta.
4. No rellenar formularios con datos sensibles sin confirmación.
5. Usar `browser_evaluate` para JS complejo.
