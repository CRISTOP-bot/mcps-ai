---
name: tmux-essentials
description: tmux esencial — sesiones, splits, persistencia. Se activa cuando se trabaja en terminal remota.
---

# Skill: tmux

## Comandos clave
- `tmux new -s nombre` / `tmux attach -t nombre`
- `Ctrl-b %` split vertical, `Ctrl-b "` horizontal
- `Ctrl-b c` nueva ventana, `Ctrl-b n/p` cambiar
- `Ctrl-b d` detach
- `Ctrl-b [` modo scroll (q sale)

## Uso típico
- Sesión para agent largo-running (worker, bridge)
- Evitar que se muera al cerrar SSH
