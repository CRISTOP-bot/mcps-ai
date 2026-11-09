---
name: systemd-services
description: Gestionar servicios systemd — status, logs, enable, edit. Se activa cuando se administra un servicio de Linux.
---

# Skill: systemd

## Comandos
```bash
systemctl --user status nombre.service
systemctl --user restart nombre.service
systemctl --user enable nombre.service   # arranque automático
journalctl --user -u nombre.service -f   # logs
systemctl --user stop nombre.service
```

## Unidad típica (~/.config/systemd/user/)
```ini
[Service]
ExecStart=/ruta/a/binario
Restart=always
```
