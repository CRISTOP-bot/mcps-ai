---
name: debug-network
description: Diagnosticar problemas de red — conectividad, puertos, DNS, proxies. Se activa cuando hay timeouts o "no se puede conectar".
---

# Skill: Diagnóstico de red

## Comandos
```bash
# Ver conexiones
ss -tuln                    # puertos abiertos
ip addr show                # interfaces
ip route                    # rutas
cat /etc/resolv.conf        # DNS

# Test de conectividad
ping -c 3 8.8.8.8
curl -s -o /dev/null -w "%{http_code}" https://github.com
nmap -p 4096,49374 localhost  # puertos OpenCode

# Proxy
echo $http_proxy $https_proxy $no_proxy
```

## Apps
- OpenCode Server: `http://127.0.0.1:4096/api/info` (o 49374)
- WhatsApp bridge: `:8080`
- MCP servers: stdio (no puerto)

## VPN/Proxy issues
- Si todo falla con timeout → resetear `no_proxy` para localhost
- `unset http_proxy https_proxy` para probar
