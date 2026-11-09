---
name: use-homeassistant
description: Controlar Home Assistant — estados, servicios, dominios, historial, eventos. Se activa cuando el usuario pide el hogar inteligente o HA.
---

# Skill: Usar Home Assistant

## Herramientas (namespace `homeassistant`)
- `ha_get_states(domain)` / `ha_get_state(entity_id)` / `ha_list_entities(domain)` / `ha_list_domains()`
- `ha_call_service(domain, service, entity_id, data_json)` — genérico
- `ha_toggle(entity_id)` / `ha_turn_on(entity_id, data_json)` / `ha_turn_off(entity_id, data_json)`
- `ha_list_services(domain)` / `ha_get_history(entity_id, hours)` / `ha_fire_event(event_type, data_json)`

## Reglas
1. HA_URL (ej: http://homeassistant.local:8123) + HA_TOKEN (long-lived token).
2. `data_json` debe ser JSON válido (ej: {"brightness_pct": 50}).
3. Confirmar antes de acciones físicas sensibles (cerraduras, alarma, calefacción).
4. Empezar con ha_list_domains() para descubrir qué hay.
