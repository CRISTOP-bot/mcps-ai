---
name: docker-containers
description: Contenerizar los MCPs con Docker — Dockerfile, compose, build. Se activa cuando el usuario quiere despliegue con Docker.
---

# Skill: Docker

## Dockerfile típico para MCP
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev
COPY . .
CMD ["python", "main.py"]
```

## docker-compose
```yaml
services:
  telegram:
    build: ./mcps/telegram-mcp
    env_file: .env
    restart: unless-stopped
```

## Comandos
```bash
docker build -t mcps-telegram .
docker run --env-file .env mcps-telegram
docker-compose up -d
docker logs -f mcps-telegram
```

## Reglas
- No copiar .env al image (usar env_file)
- Imagen slim/alpine
- Usuario non-root
