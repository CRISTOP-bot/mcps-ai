---
name: security-essentials
description: Seguridad esencial en el proyecto — inputs, outputs, secrets, dependencias. Se activa siempre.
---

# Skill: Seguridad esencial

## Input
- Validar y sanitizar siempre
- Nunca confiar en input externo

## Output
- No imprimir secrets
- No imprimir paths del sistema innecesarios

## Dependencies
- `uv lock` fija versiones
- Revisar CVEs antes de actualizar
- Mínimos paquetes necesarios

## Secrets
- `.env` nunca commiteado
- Rotar al salir del equipo
- Un secret por propósito

## Red
- HTTPS siempre
- Certificados válidos
- localhost binding (127.0.0.1) para servicios internos
