---
name: network-security-basics
description: Seguridad de red básica — puertos, firewall, exposición. Se activa cuando se expone un servicio.
---

# Skill: Seguridad de red

## Checklist al exponer un servicio
- [ ] ¿Solo localhost? `ss -tuln` — bind 127.0.0.1 si es interno
- [ ] ¿Firewall? `ufw status` (Linux)
- [ ] ¿Auth? Todo lo que salga de localhost requiere token
- [ ] ¿TLS? HTTPS obligatorio para lo público
- [ ] ¿Logs? Sin datos sensibles
