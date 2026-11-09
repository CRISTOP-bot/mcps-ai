---
name: env-management
description: Gestionar variables de entorno y .env correctamente. Se activa al configurar o depurar MCPs.
---

# Skill: Environment management

## Reglas
1. Nunca hardcodear secrets
2. Usar `.env` + `python-dotenv`
3. `.env.example` con placeholders
4. Defaults seguros: `os.getenv("VAR", "default")`

## app.py
```python
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

## .env.example
```bash
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USERS=
AI_BASE_URL=http://127.0.0.1:4096
```

## Debug
```bash
# Ver qué se carga
cat .env | grep -v "=$"
# Validar
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(list(os.environ.keys()))"
```
