---
name: documentation
description: Documentar código y proyecto efectivamente. Se activa cuando el usuario pide docs.
---

# Skill: Documentación

## Niveles
1. **README** — visión general, instalación, uso
2. **WIKI.md** — documentación completa
3. **Docstrings** — API de cada función
4. **Inline comments** — solo lógica compleja
5. **CONTRIBUTING.md** — cómo contribuir

## Docstring útil
```python
async def send_message(chat_id: str, text: str):
    """Send a text message via Telegram Bot API.
    
    Args:
        chat_id: Numeric chat ID (e.g., '8837193180')
        text: Message content (max 4096 chars)
    
    Returns:
        dict with status/response from Telegram API
    
    Raises:
        HTTPException on API failure
    """
```

## README sections
- Título + badges
- Qué es (1 línea)
- Features
- Instalación (npx o manual)
- Uso
- Comandos
- Contribuir
- Licencia
