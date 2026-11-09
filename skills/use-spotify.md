---
name: use-spotify
description: Controlar Spotify — búsqueda, play/pause, volumen, playlists, dispositivos. Se activa cuando el usuario pide música o Spotify.
---

# Skill: Usar Spotify

## Herramientas (namespace `spotify`)
- `spotify_search(query, search_type, limit)` — track|artist|album|playlist
- `spotify_now_playing()` / `spotify_play` / `spotify_pause` / `spotify_next` / `spotify_previous`
- `spotify_set_volume(0-100)` / `spotify_queue(track_uri)` / `spotify_transfer_playback(device_id)`
- `spotify_list_playlists()` / `spotify_playlist_tracks(playlist_id)` / `spotify_create_playlist(name)`
- `spotify_list_devices()` / `spotify_saved_tracks(limit)`

## Reglas
1. Requiere token OAuth con refresh (ver README del MCP). Si 401 → pedir re-autenticar.
2. Para "pon música": buscar → tomar primer track → `spotify_queue` o `spotify_play(context_uri)`.
3. Si no hay dispositivo activo, listar dispositivos y preguntar.
