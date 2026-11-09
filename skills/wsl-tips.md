---
name: wsl-tips
description: Tips para WSL2 — rutas, systemd, integración con Windows. Se activa cuando el usuario trabaja en WSL.
---

# Skill: WSL2

## Esenciales
- Rutas: /mnt/c/... = C:\
- systemd habilitado en /etc/wsl.conf ([boot] systemd=true)
- Memoria: limitar en .wslconfig ([wsl2] memory=4GB)
- Windows Terminal + tmux = entorno completo

## Red
- WSL2 tiene su propia IP; localhost comparte con Windows en la config por defecto
