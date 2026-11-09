---
name: deploy-checklist
description: Checklist de despliegue — antes, durante, después. Se activa cuando se va a desplegar algo.
---

# Skill: Deploy checklist

## Antes
- [ ] CI verde, tests pasan
- [ ] Backup / rollback plan
- [ ] Ventana de mantenimiento si aplica

## Durante
- [ ] Monitorear logs en vivo
- [ ] Health check: endpoint responde

## Después
- [ ] Verificar métricas volvieron a normal
- [ ] Comunicar estado a afectados
- [ ] Documentar desviaciones
