---
name: use-filesystem
description: Operaciones de archivos en el sistema — leer, escribir, buscar, copiar, mover, permisos. Se activa cuando el usuario pide archivos/directorios.
---

# Skill: Usar Filesystem

## Herramientas disponibles (namespace `filesystem`)
- `fs_read_file(path, encoding)` — leer archivo
- `fs_write_file(path, content, append)` — escribir/append
- `fs_list_dir(path, pattern, show_hidden)` — listar directorio
- `fs_search_files(directory, pattern, max_results)` — buscar por nombre/glob
- `fs_search_content(directory, query, file_pattern, max_results)` — grep en contenido
- `fs_tree(path, max_depth, show_hidden)` — árbol de directorios
- `fs_hash(path, algorithm)` — sha256/md5/sha1
- `fs_copy(source, destination)` / `fs_move_file` / `fs_delete_file`
- `fs_chmod(path, mode)` — cambiar permisos
- `fs_disk_usage(path)` — espacio en disco
- `fs_file_info(path)` — metadatos (tamaño, fechas, permisos)
- `fs_grep(path, pattern, file_pattern, max_results)` — grep con regex

## Reglas de uso
1. Solo tiene acceso a `$HOME` y `/tmp` por diseño (seguridad).
2. No borrar archivos sin confirmación explícita del usuario.
3. Antes de sobrescribir, confirmar.
4. Para buscar en todo el directorio usar `fs_tree` o `fs_list_dir` con glob.
5. Para buscar texto en código usar `fs_grep` o `fs_search_content`.
