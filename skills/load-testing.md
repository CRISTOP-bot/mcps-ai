---
name: load-testing
description: Pruebas de carga básicas para servicios. Se activa cuando se valida capacidad.
---

# Skill: Load testing

## Herramientas
- `hey -n 1000 -c 50 URL`
- `k6 run script.js`
- `ab -n 1000 -c 50 URL`

## Métricas
- p95/p99 latencia, requests/s, error rate
- Establecer baseline antes de optimizar
