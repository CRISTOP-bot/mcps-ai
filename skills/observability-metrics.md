---
name: observability-metrics
description: Métricas, logs y trazas — qué medir y cómo. Se activa cuando se instrumenta un servicio.
---

# Skill: Observabilidad

## Pilares
1. **Métricas** — contadores, histogramas (latencia), gauges (RAM)
2. **Logs** — estructurados, con contexto (request_id)
3. **Trazas** — path de una request a través de servicios

## Qué medir en MCPs/workers
- requests/min, errores/min, duración p50/p95
- tokens por modelo (consumo), tasa de fallback

## Herramientas
- Prometheus + Grafana, Loki, OpenTelemetry
