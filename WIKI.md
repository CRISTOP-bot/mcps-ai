MCPs-AI — Wiki Técnica Completa
=================================
Repositorio: https://github.com/CRISTOP-bot/mcps-ai
Estado: 8 MCPs, 7 agentes soportados, 137+ tools, CLI npm publicado
Última actualización: 9 noviembre 2026


TABLA DE CONTENIDOS
-------------------
1. Arquitectura general
2. MCP: Telegram (agente remoto)
3. MCP: WhatsApp (bridge + servidor Python)
4. MCP: Minecraft (RCON)
5. MCP: Gmail (OAuth2 Google API)
6. MCP: Filesystem
7. MCP: System (info de la máquina)
8. MCP: Web (búsqueda + fetch)
9. MCP: Browser (Playwright)
10. CLI: mcps-ai (instalador/actualizador)
11. Login con GitHub (device flow / gh CLI)
12. Sistema de tokens y secretos
13. Backup/Restore de credenciales (Gist privado)
14. CI/CD (GitHub Actions)
15. Publicación en npm (publish)
16. Estructura de carpetas y por qué
17. Comandos y configuración por agente
18. Seguridad: qué nunca va a git
19. Diagnóstico y solución de problemas
20. Changelog de la sesión de trabajo


1. ARQUITECTURA GENERAL
-----------------------

mcps-ai/
├── mcps/                    # 8 MCP servers (Python/FastMCP + Playwright)
│   ├── telegram-mcp/        # Agente remoto OpenCode-Telegram (24/7 worker)
│   ├── whatsapp-mcp/        # Bridge Go (whatsmeow) + servidor FastMCP Python
│   ├── minecraft-mcp/       # RCON a servidor Minecraft
│   ├── gmail-mcp/           # Google Gmail API OAuth2
│   ├── filesystem-mcp/      # Operaciones de archivos confinadas a $HOME y /tmp
│   ├── system-mcp/          # Info de la máquina (CPU/RAM/disco/red/batería)
│   ├── web-mcp/             # Búsqueda Bing scrape + Web fetch + clima
│   └── browser-mcp/         # Chrome/Chromium controlado vía Playwright
├── agents/                  # Instrucciones de configuración por agente
├── cli/                     # npm package "mcps-ai" (bin: mcps-ai)
├── install.md               # Guía para agentes AI
├── package.json             # v1.1.0, files: cli + mcps + agents + README/etc
├── setup.sh                 # Instalación bash (Linux + macOS)
└── .github/workflows/ci.yml # Tests en cada push

Cada MCP es un proceso independiente que habla MCP (JSON-RPC sobre stdio).
Los clientes (OpenCode, Claude Desktop, Kiro, etc.) lanzan el proceso y le envían
tools/list, tools/call, resources/list, etc.


2. TELEGRAM-MCP — Agente Remoto
-------------------------------
Archivo principal: mcps/telegram-mcp/telegram_worker.py
Tests: 14 (test_session_store.py 9, test_opencode_client.py 5)

Flujo:
  Usuario → Telegram → @orqelis_bot
  → Worker long-polling (getUpdates, timeout 30s)
  → Filtra por TELEGRAM_ALLOWED_USERS (solo Cristopher 8837193180)
  → EnCola en TaskManager (cola por chat, concurrencia máx 3)
  → Crea/Reusa sesión de OpenCode (ses_xxx)
  → Envía prompt via POST /api/session/{id}/prompt
  → Pollea mensajes cada 2s hasta ver idle(outcome=succeeded)
  → Envía cada asistente encontrado como mensaje nuevo a Telegram

Características:
  - Sin timeout (REQUEST_TIMEOUT=0) para tareas largas
  - 11 modelos de fallback gratuitos:
    deepseek-v4.1-flash-free, glm-5.3-flash-free, iceman-free, inkling-2-small-free,
    crouton-alpha-free, flint-40b-free, nemotron-3.5-super-vl-free, beam-free,
    mimo-v2.6-flash-free, nemotron-3.5-lightning-free, big-pickle
  - Si el modelo activo se agota, cambia solo y reintenta con el siguiente
  - Convierte Markdown → texto plano antes de enviar (strip_markdown)
  - Envia progreso en tiempo real: tool calls, comandos, output
  - Screen lock desactivado en la laptop
  - Linger habilitado → worker corre aunque no haya sesión gráfica
  - Servicios systemd: opencode-server.service + opencode-telegram-worker.service

Problemas resueltos en esta sesión:
  1. Stale responses: el código devolvía la respuesta anterior. Solución: rastrear
     IDs de mensajes, no counts (los IDs son únicos).
  2. Paginación: los mensajes llegan newest-first; se interpretaba al revés.
  3. Database migration: sessions.opencode_session_id → ai_session_id.
  4. Task duplication: ensure_future → create_task (asyncio).
  5. Token loss on CLI upgrade: mergeServers ahora preserva config existente + tokens.
  6. No markdown: parse_mode=Markdown quitado + strip_markdown() para legibilidad.

Config relevante:
  TELEGRAM_BOT_TOKEN = <token-bot-creado-con-@BotFather> (nunca en git)
  TELEGRAM_ALLOWED_USERS = 8837193180
  AI_BASE_URL = http://127.0.0.1:49374 (OpenCode server local)
  AI_MODEL_ID = deepseek-v4.1-flash-free
  AI_PASSWORD = <password-opencode-server> (nunca en git)


3. WHATSAPP-MCP
---------------
Componentes:
  1. Go bridge (whatsmeow) en whatsapp-bridge/main.go
  2. Python server en whatsapp-mcp-server/main.py (FastMCP)

Flujo:
  whatsmeow conecta como dispositivo vinculado a tu WhatsApp personal
  → QR scan en primer arranque (o token si ya existe auth.db)
  → Expone 12 funciones: send_message, send_file, get_chat, download_media, etc.
  → El servidor Python las expone como tools MCP

Config:
  - Token de sesión: whatsapp.db (SQLite local, gitignored)
  - Phone: +584120000000 (Cristopher)


4. MINECRAFT-MCP — RCON
------------------------
Cliente: mcps/minecraft-mcp/rcon.py
Servidor: cualquier servidor Java 1.20+ con enable-rcon=true
Credenciales en .env: MC_HOST, MC_PORT, MC_RCON_PASSWORD

21 herramientas: give, tp, weather, time, gamemode, difficulty,
summon, effect, locate, setblock, kill all, give all, experience, list spawn


5. GMAIL-MCP — Google OAuth2
-----------------------------
Cliente: googleapiclient en mcps/gmail-mcp/main.py
Scopes: readonly, send, modify, labels

Flujo de autenticación:
  1. Google Cloud Console → Crear proyecto
  2. Habilitar Gmail API
  3. Crear credenciales OAuth 2.0 (Desktop app)
  4. Descargar credentials.json
  5. Ejecutar python gmail_auth.py → abre navegador → autoriza
  6. Se genera token.json (refresh token + access token)

13 herramientas: profile, list, read, send, reply, search, labels, star, archive, forward, thread, unread


6. FILESYSTEM-MCP
-----------------
Sólo permite acceso dentro de:
  ~/ y /tmp

13 herramientas: read, write, list, search, grep, tree, hash, chmod, copy, delete, move, disk_usage


7. SYSTEM-MCP — Info de la máquina
-----------------------------------
Cross-platform (Linux/macOS detectado en runtime):
  - Linux: lscpu, free -h, ip addr, ss, systemctl, upower, sensors
  - macOS: sysctl, vm_stat, ifconfig, launchctl, pmset, powermetrics
  - Windows: wmic, tasklist, netstat

18 herramientas: sys_info, sys_processes, sys_top, sys_memory, sys_disk, sys_network, sys_ports, kill, env_vars, logs, services, cpu, who, uptime, kill_by_name, failed, temperature, battery


8. WEB-MCP — Búsqueda y Fetch
-------------------------------
Motor: Bing (HTML scrape) + DuckDuckGo (HTML scrape, fallback)
Por qué no API: DuckDuckGo bloquea requests automáticos sin CAPTCHA.
Bing funciona con HTML + parseo de h2 > a (title + URL) + snippets con CSS class.

4 herramientas: web_search, web_fetch, web_news, web_weather


9. BROWSER-MCP — Playwright
-----------------------------
Control de Chrome/Chromium headless via Playwright.
17 herramientas: navigate, click, fill, type, press, text, html, screenshot, evaluate, wait, select, scroll, back, forward, reload, get_links, close


10. CLI: mcps-ai
----------------
Instalar:  npx github:CRISTOP-bot/mcps-ai install
Publicar:  npm publish (después de npm login)

ms-ai/
├── bin/mcps-ai.js          # Entry point
├── src/main.js             # Dispatcher de comandos
├── src/agents.js           # Detección de agentes + escritura de configs
├── src/install.js          # Lógica de instalación/update/status/doctor
├── src/github.js           # GitHub auth (gh CLI / token) + Gist backup/restore
└── package.json            # name=mcps-ai, bin=mcps-ai

Comandos:
  install [agentes...]  # Detecta/instala/configura
  update                # Actualiza sin perder .env ni configs
  status                # Estado
  doctor                # Diagnóstico
  login / logout        # GitHub auth (usa gh CLI o token)
  backup / restore      # Gist privado para credenciales

Merge seguro: cuando se escribe la config de un agente, se lee la config EXISTENTE
y se fusionan (nuevas tools se agregan, tools existentes con directory válido se preservan,
env vars existentes se preservan, bloques rotos se reemplazan). Los .bak nunca se borran.


11. LOGIN CON GITHUB
--------------------
Vía gh CLI: si está instalado y logueado, usa `gh auth token` automáticamente.
Vía token manual: el usuario pega un Personal Access Token (github.com/settings/tokens).
  Scopes necesarios: gist, read:user.

Flujo dispositivo (device flow) estaba presente pero se cambió a gh CLI porque
no hay OAuth app pública registrada con device flow habilitado.

El token se guarda en ~/.mcps-ai/github-token con permisos 600.


12. SISTEMA DE TOKENS Y SECRETOS
---------------------------------
NUNCA en git: tokens, passwords, .env, credentials.json, token.json, key4.db, auth.db
gitignore bloquea: **/.env, **/.venv/, __pycache__/, *.pyc, data/, *.db

Reglas:
  1. .env.example sí se versiona (plantilla con keys pero sin valores reales)
  2. Los .env reales solo viven en el disco del usuario
  3. los .pyc / .venv nunca se versiona el binario
  4. Tokens de API nunca en strings de código; siempre en env vars o .env
  5. Los permisos de .env se fijan en 600 al crearlo

Archivos con datos sensibles detectados durante la sesión:
  ~/.npmrc                       → //registry.npmjs.org/:_authToken=npm_xxx  (600)
  ~/.opencode/bin/opencode       → binario (no editable)
  ~/.config/opencode/opencode.json → config MCP (sin tokens)
  ~/.kiro/settings/mcp.json      → config Kiro (sin tokens)
  ~/.config/opencode/service.json → password OpenCode Server (600, no en git)
  ~/mcp-servers/telegram-mcp/.env → TELEGRAM_BOT_TOKEN, AI_PASSWORD (600)
  ~/mcp-servers/minecraft-mcp/.env → MC_RCON_PASSWORD (600)
  ~/mcp-servers/gmail-mcp/.env    → GMAIL_TOKEN path (600)


13. BACKUP/RESTORE DE CREDENCIALES (GIST PRIVADO)
---------------------------------------------------
Comando:  mcps-ai backup
Acciones:
  1. Obtiene token de ~/.mcps-ai/github-token (o gh auth token)
  2. Recolecta: todos los .env, credentials.json, token.json, opencode.json, kiro-mcp.json
  3. Sube como Gist privado (description: "mcps-ai credentials backup (private)")
  4. Si existe gist con ese nombre → PATCH, sino POST
  5. Stack: PATCH /gists/{id} o POST /gists { description, public:false, files:{...} }

Comando:  mcps-ai restore
  1. Busca el gist por description
  2. Lista archivos
  3. Restaura a la máquina local (con .bak si existe)


14. CI/CD — GitHub Actions
---------------------------
Archivo: .github/workflows/ci.yml
Jobs: test-telegram, test-minecraft, test-gmail-import, test-filesystem-import,
      test-system-import, test-web-import, test-browser-import
Cada uno: checkout → setup-uv → uv sync → importar módulo o correr pytest
Último estado: todos passing


15. PUBLICACIÓN EN NPM
-----------------------
Name: mcps-ai
Token: ~/.npmrc tiene //registry.npmjs.org/:_authToken=npm_...
Error común: EO EUTH — el token está expirado/no tiene permisos
npm publish falla con 403 si:
  - 2FA requerido y no se pasa --otp
  - token granular sin Bypass 2FA
  - scope incorrecto

Solución: crear Granular Access Token con Publish + Bypass 2FA en npmjs.com/settings/tokens


16. ESTRUCTURA DE CARPETAS — POR QUÉ
--------------------------------------
- mcps/ canónico (no duplicar por agente): antes cada agente tenía copia → 256MB repo
  ahora 432KB, sin drift entre copias
- agents/ solo instrucciones (README): los agentes se configuran por JSON, no por código
- cli/: el instalador es el producto principal (npm package "mcps-ai")
- install.md: guía en lenguaje natural para agentes AI
- CI en cada push: garantiza que imports y tests pasen en cada commit


17. COMANDOS POR AGENTE
-----------------------
Claude Desktop:
  Unir en ~/.config/claude/claude_desktop_config.json

Claude Code:
  Unir en .mcp.json en la raíz del proyecto

Cursor:
  Unir en .cursor/mcp.json en la raíz del proyecto

Kiro:
  Unir en ~/.kiro/settings/mcp.json

OpenCode:
  Unir en ~/.config/opencode/opencode.json

OpenClaw:
  Unir en ~/.openclaw/config.json → mcp.servers

Windsurf:
  Unir en ~/.codeium/windsurf/mcp_config.json

Formato:
  Cada bloque es una entrada bajo mcpServers (o mcp.servers) con:
  {
    "command": "uv",
    "args": ["--directory", "<path>/mcps/<name>", "run", "main.py"],
    "env": { ... }
  }


18. SEGURIDAD — QUÉ NUNCA VA A GIT
-----------------------------------
- .env, .env.*
- credentials.json, token.json
- *.db (whatsapp.db, auth.db, telegram.db)
- .venv/, __pycache__/, *.pyc
- .npmrc, .git-credentials, id_rsa, known_hosts
- service.json (OpenCode Server password)
- *.bak.*


19. DIAGNÓSTICO Y SOLUCIÓN DE PROBLEMAS
-----------------------------------------
Problema → Causa → Fix
─────────────────────────────────────────────────
Telegram no responde → Worker caído o update_id duplicado → reiniciar servicio, borrar sqlite task_state
No responde respuesta anterior → prev_count bug → rastrear IDs, no counts
Gmail no autentica → token.json expirado → re-ejecutar gmail_auth.py
Minecraft RCON → wrong password → verificar .env, server enable-rcon=true
npm publish 403 → token sin Bypass 2FA → crear Granular token
npx mcps-ai hang → install lifecycle script → removido, usar npx github:... o global
Browser "Executable doesn't exist" → playwright browsers no instalados → uv run playwright install chromium
System MCP on macOS fails sensors → no existe → fallback a powermetrics con sudo


20. CHANGELOG DE LA SESIÓN
----------------------------
- Creado MCP Telegram completo (bot + worker OpenCode)
- Reparado bug "stale response" (IDs en vez de counts)
- Auto-cambio de modelo cuando se acaban tokens (11 fallbacks)
- strip_markdown para texto plano en Telegram
- Screen lock deshabilitado + linger habilitado
- 8 MCPs totales: telegram, whatsapp, minecraft, gmail, filesystem, system, web, browser
- CLI "mcps-ai" publicado en npm (instalación detecta agentes, preserva config)
- Login con GitHub (gh CLI o token) + Gist privado de backup
- Reestructura: mcps/ único (sin duplicar por agente) → 432KB vs 256MB
- CI 100% passing
- macOS support completo (system-mcp y launchd)
- .gitignore comprehensivo: .env, .venv, __pycache__, *.db, etc.
- Sin secretos en git (verificado git grep)


NOTAS FINALES
-------------
Este documento NO contiene credenciales.
Si encuentras un token en algún archivo, el .gitignore debería impedirlo;
si no, reportarlo y rotarlo inmediatamente.
El token npm en ~/.npmrc está en chmod 600, nunca se imprime.
