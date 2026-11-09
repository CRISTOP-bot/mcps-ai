# Minecraft MCP Server

Controla un servidor de Minecraft desde IA/Telegram mediante RCON.

## Herramientas disponibles

| Tool | Descripción |
|---|---|
| `mc_status` | Estado del servidor (jugadores online) |
| `mc_players` | Lista de jugadores conectados |
| `mc_say` | Enviar mensaje al chat del servidor |
| `mc_give` | Dar items a un jugador |
| `mc_tp` | Teletransportar jugador |
| `mc_weather` | Cambiar clima (clear/rain/thunder) |
| `mc_time` | Cambiar hora (day/night/noon/midnight) |
| `mc_gamemode` | Cambiar modo de juego |
| `mc_command` | Ejecutar cualquier comando |
| `mc_locate` | Localizar estructuras |
| `mc_summon` | Invocar entidades |
| `mc_effect` | Dar efectos de poción |
| `mc_difficulty` | Cambiar dificultad |

## Configuración del servidor Minecraft

En `server.properties`:
```
enable-rcon=true
rcon.port=25575
rcon.password=tu_password
```

## Variables de entorno

```
MC_HOST=localhost
MC_PORT=25575
MC_RCON_PASSWORD=tu_password
MC_PLAYER=TuUsername
```

## Ejecución

```bash
cd /home/cristopher/mcp-servers/minecraft-mcp
uv run python main.py
```

## Nota

El servidor Minecraft debe estar corriendo con RCON habilitado. El MCP se conecta via RCON (puerto 25575 por defecto).
PYEOF
echo "README creado"