# AI Telegram Remote Agent

Transforma tu computadora en un servidor personal de IA controlable remotamente mediante Telegram.

## Arquitectura

```
telegram-mcp/
├── main.py                  # MCP server (FastMCP, stdio)
├── telegram_worker.py       # Persistent Telegram worker
├── ai_client.py       # Async HTTP client for AI Server
├── session_store.py         # SQLite persistence
├── task_manager.py          # Task queue and processing
├── config.py                # Configuration management
├── .env                     # Environment variables
├── .env.example             # Template
├── data/
│   └── telegram.db          # SQLite database
├── tests/                   # Automated tests
└── README.md
```

## Componentes

### 1. AI Server
Servidor HTTP que expone la API de IA. Debe estar corriendo permanentemente.

### 2. Telegram Worker
Proceso persistente que:
- Recibe mensajes de Telegram via long polling
- Los envía a AI Server
- Retorna las respuestas a Telegram
- Gestiona sesiones por chat
- Maneja autorización, deduplicación y cola de tareas

### 3. MCP Server (main.py)
Servidor MCP que expone herramientas de Telegram para uso dentro de IA.

## Instalación

### Prerrequisitos
- Python 3.12+
- uv (gestor de paquetes)
- IA CLI

### Setup

```bash
cd /home/cristopher/mcp-servers/telegram-mcp
uv sync
cp .env.example .env
# Editar .env con tus valores
```

### Configurar variables de entorno

```bash
# .env
TELEGRAM_BOT_TOKEN=tu_token_de_botfather
TELEGRAM_ALLOWED_USERS=123456789  # tu user ID de Telegram
AI_BASE_URL=http://127.0.0.1:4096
AI_PASSWORD=tu_password_de_ai
AI_DIRECTORY=/home/cristopher
DATABASE_PATH=./data/telegram.db
REQUEST_TIMEOUT=120
```

## Ejecución

### 1. Iniciar AI Server
```bash
opencode serve --port 4096 --hostname 127.0.0.1
```

### 2. Iniciar Telegram Worker
```bash
uv run python telegram_worker.py
```

### 3. MCP Server (automático via IA)
El MCP server se inicia automáticamente cuando IA lo necesita (configurado en opencode.json).

## Comandos de Telegram

- `/start` - Iniciar el agente
- `/help` - Mostrar ayuda
- `/status` - Estado del sistema
- `/new` - Crear nueva sesión de IA
- `/cancel` - Cancelar generación activa

Los mensajes normales se envían directamente a IA.

## Seguridad

- Solo usuarios en `TELEGRAM_ALLOWED_USERS` pueden usar el bot
- Si no se configuran usuarios, se rechaza todo por defecto
- No se exponen tokens en logs
- AI Server solo escucha en localhost
- No se abre ningún puerto al exterior

## Inicio automático (systemd)

### Instalar servicios
```bash
mkdir -p ~/.config/systemd/user
cp ai-server.service ~/.config/systemd/user/
cp telegram-worker.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable ai-server telegram-worker
systemctl --user start ai-server telegram-worker
```

### Consultar estado
```bash
systemctl --user status telegram-worker
systemctl --user status ai-server
```

### Ver logs
```bash
journalctl --user -u telegram-worker -f
journalctl --user -u ai-server -f
```

### Evitar suspensión de laptop
```bash
# Deshabilitar suspensión
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
# O configurar en GNOME: Settings > Power > Screen Blank = Never
```

## Pruebas

```bash
uv run python -m pytest tests/ -v
```

## Solución de problemas

### AI Server no responde
- Verificar que está corriendo: `curl -u ai:PASSWORD http://127.0.0.1:4096/api/info`
- Revisar logs: `journalctl --user -u ai-server -f`

### Worker no recibe mensajes
- Verificar token de Telegram
- Verificar que no hay otro proceso usando getUpdates
- Revisar logs: `journalctl --user -u telegram-worker -f`

### Sesión no se crea
- Verificar que AI Server está accesible
- Verificar AI_PASSWORD en .env
- Revisar logs del worker

## Licencia

MIT
PYEOF
echo "README creado"