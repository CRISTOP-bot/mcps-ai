---
name: home-assistant-automations
description: Diseñar automatizaciones en Home Assistant — triggers, condiciones, acciones. Se activa cuando el usuario quiere automatizar el hogar.
---

# Skill: Automatizaciones HA

## Estructura
```yaml
trigger:  # qué dispara (hora, sensor, evento)
condition: # filtros opcionales
action:   # qué hacer (llamar servicios)
```

## Ejemplos
- Luces al atardecer: trigger sun.sun → action light.turn_on
- Apagar todo al salir: trigger person.x → homeassistant.turn_off
- Aviso de puerta: trigger binary_sensor → notify

## Con MCP
`ha_call_service("automation", "trigger", ...)` para probar
