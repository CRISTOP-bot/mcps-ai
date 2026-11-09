---
name: regex-mastery
description: Regex práctico — grupos, lookahead, flags. Se activa cuando el usuario pide un patrón regex.
---

# Skill: Regex

## Referencia rápida
- `\d+` dígitos, `\w+` palabra, `\s+` espacio
- `(grupo)` capturar, `(?:grupo)` no capturar
- `(?=...)` lookahead positivo, `(?!...)` negativo
- Flags: i (case-insensitive), m (multiline), s (dotall)
- Anclas `^ $` con multiline

## Probar
`echo "texto" | grep -oE 'patrón'` o regex101.com
