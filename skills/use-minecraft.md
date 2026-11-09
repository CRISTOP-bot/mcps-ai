---
name: use-minecraft
description: Usar Minecraft por RCON — comandos de jugador, mundo, clima, dificultad, admin. Se activa cuando el usuario pide controlar un servidor Minecraft.
---

# Skill: Usar Minecraft RCON

## Herramientas disponibles (namespace `minecraft`)
- `mc_command(command)` — ejecutar cualquier comando raw
- `mc_give(player, item, count)`, `mc_give_all(item, count)` — dar items
- `mc_tp(player, x, y, z)`, `mc_tp_all(x, y, z)` — teletransportar
- `mc_weather(weather_type)`, `mc_weather_time_clear()` — clima
- `mc_time(time_value)` — hora del día (day, night, noon, midnight)
- `mc_gamemode(player, mode)` — survival, creative, adventure, spectator
- `mc_difficulty(difficulty)` — peaceful, easy, normal, hard
- `mc_summon(entity, x, y, z)` — invocar mobs
- `mc_effect(player, effect, duration, amplifier)` — efectos de poción
- `mc_locate(structure)` — localizar estructuras
- `mc_status()`, `mc_players()` — info del servidor y jugadores
- `mc_setblock`, `mc_kill_all`, `mc_experience`, `mc_list_spawn`, `mc_list_dimension`

## Reglas
1. Verificar el servidor con `mc_status` antes de mandar comandos.
2. Los comandos usan sintaxis nativa de Minecraft (`/give`, `/tp`, `/weather`...).
3. `mc_command("give @p diamond 1")` es válido como fallback.
4. Respetar reglas del servidor: no griefing, no borrar mundo sin permiso.
