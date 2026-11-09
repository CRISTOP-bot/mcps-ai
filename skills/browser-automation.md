---
name: browser-automation
description: Automatizar tareas web complejas — login, scraping, formularios, testing. Se activa cuando el usuario pide automatizar un flujo web.
---

# Skill: Automatización de browser

## Flujo típico de automatización
```python
navigate(url) → get_text(selector) → fill(selector, valor) → click(selector) → wait(selector) → screenshot()
```

## Login con formulario
1. `browser_navigate(url)` — abrir página de login
2. `browser_get_text()` — leer estructura
3. `browser_fill("#email", "user@mail.com")`
4. `browser_fill("#password", "pass")`
5. `browser_click("button[type=submit]")`
6. `browser_wait(".dashboard")` — esperar el panel
7. `browser_screenshot()` — evidencia

## Scraping
- `browser_get_text()` para contenido visible
- `browser_evaluate("return document.title")` para JS
- `browser_get_links()` para extraer URLs

## Testing automatizado
1. Navega a la página
2. Rellena form
3. Submit
4. Verifica elementos visibles
5. Screenshot como evidencia
