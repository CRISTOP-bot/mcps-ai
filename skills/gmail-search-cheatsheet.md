---
name: gmail-search-cheatsheet
description: Sintaxis de búsqueda avanzada de Gmail API. Se activa cuando el usuario quiere buscar correos específicos.
---

# Skill: Gmail search cheatsheet

## Búsqueda
```
from:john@example.com          # de alguien
to:me                           # para mí
subject:meeting                 # asunto
has:attachment                  # con adjuntos
is:unread                       # no leídos
is:starred                      # destacados
is:important                    # importantes
label:work                      # etiqueta "work"
after:2026/01/01                # después de fecha
before:2026/12/31               # antes de fecha
newer_than:7d                   # últimos 7 días
older_than:30d                  # más de 30 días
filename:pdf                    # adjuntos PDF
```

## Combinaciones
```
from:boss is:unread after:2026/11/01
has:attachment newer_than:7d label:invoices
is:starred subject:factura
```
