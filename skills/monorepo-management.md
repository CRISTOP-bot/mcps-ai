---
name: monorepo-management
description: Gestionar monorepos — workspaces, dependencias compartidas. Se activa cuando el proyecto crece en un solo repo.
---

# Skill: Monorepo

## Opciones
- **npm workspaces** — packages/* comparten node_modules
- **uv workspace (Python)** — miembros en pyproject
- **Just/Make** — comandos unificados

## Estructura mcps-ai
- mcps/ = servidores independientes (uno por MCP)
- cli/ = paquete npm
- skills/ = contenido para agentes
