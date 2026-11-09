# Gmail MCP Server

Controla tu Gmail desde cualquier agente de IA via MCP.

## Herramientas disponibles (15)

| Tool | Descripción |
|---|---|
| `gmail_profile` | Perfil del usuario (email, total mensajes) |
| `gmail_list_emails` | Listar emails (con filtros por label) |
| `gmail_read_email` | Leer email completo (cuerpo, adjuntos) |
| `gmail_send_email` | Enviar email (texto o HTML) |
| `gmail_reply` | Responder a un email |
| `gmail_search` | Buscar emails (sintaxis Gmail) |
| `gmail_list_labels` | Listar etiquetas/carpetas |
| `gmail_mark_read` | Marcar como leído |
| `gmail_mark_unread` | Marcar como no leído |
| `gmail_delete_email` | Mover a papelera |
| `gmail_create_label` | Crear etiqueta |
| `gmail_add_label` | Agregar etiqueta a email |
| `gmail_unread_count` | Contar emails no leídos |

## Configuración

### 1. Google Cloud Console

1. Ve a https://console.cloud.google.com/
2. Crea un proyecto
3. Habilita la Gmail API
4. Crea credenciales OAuth 2.0 (Desktop app)
5. Descarga como `credentials.json`

### 2. Autenticar

```bash
cd gmail-mcp
uv sync
cp .env.example .env
# Editar .env con las rutas correctas
python gmail_auth.py  # Abre navegador para autenticar
```

### 3. Ejecutar

```bash
uv run python main.py
```

## Variables de entorno

```
GMAIL_CREDENTIALS=credentials.json
GMAIL_TOKEN=token.json
GMAIL_USER=me
```

## Búsqueda (sintaxis Gmail)

- `from:john@example.com` - De un remitente
- `to:me` - Enviados a ti
- `subject:meeting` - Asunto contiene
- `is:unread` - No leídos
- `has:attachment` - Con adjuntos
- `after:2024/01/01` - Después de fecha
- `label:important` - Con etiqueta
PYEOF
echo "README creado"