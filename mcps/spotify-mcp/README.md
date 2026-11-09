# Spotify MCP Server

MCP server that lets an assistant control Spotify playback and manage the user's library/playlists via the Spotify Web API. Authentication uses the Authorization Code with Refresh Token flow.

## Setup

### 1. Create a Spotify app

1. Go to <https://developer.spotify.com/dashboard> and log in.
2. Click **Create app**, give it any name and description.
3. Set the **Redirect URI** to `http://localhost` (any path works, e.g. `http://localhost:3000/callback`, as long as it is added to the app).
4. Under **Which API/SDKs are you planning to use?** select **Web API**.
5. Save, then note the app's **Client ID** and **Client Secret**.
6. In the app settings, add these scopes to your authorization request:
   - `playlist-modify-public`
   - `playlist-modify-private`
   - `user-read-playback-state`
   - `user-modify-playback-state`
   - `user-read-currently-playing`
   - `user-library-read`
   - `playlist-read-private`
   - `user-read-playback-position`

### 2. Get a refresh token (Authorization Code flow)

Follow the official guide: <https://developer.spotify.com/documentation/web-api/tutorials/code-flow>

Summary:

1. Build an authorize URL and open it in your browser:

   ```
   https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&scope=playlist-modify-public%20playlist-modify-private%20user-read-playback-state%20user-modify-playback-state%20user-read-currently-playing%20user-library-read%20playlist-read-private%20user-read-playback-position
   ```

2. Approve access. Spotify redirects to `http://localhost/?code=AUTH_CODE` — copy the `code` value from the URL (it is single-use and expires quickly).
3. Exchange the code for tokens:

   ```bash
   curl -X POST https://accounts.spotify.com/api/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -u "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" \
     -d "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=http://localhost"
   ```

4. Copy the `refresh_token` from the response. It does not expire (unless revoked) and is used by this server to mint short-lived access tokens.

### 3. Configure environment

Copy `.env.example` to `.env` and fill in the values:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REFRESH_TOKEN=your_refresh_token
```

Or export them as environment variables.

### 4. Install and run

```bash
uv sync
uv run python main.py
```

The server runs over stdio. To register it with an MCP client, point the client at `uv run python /path/to/spotify-mcp/main.py`.

## Tools

| Tool | Description |
| --- | --- |
| `spotify_search` | Search tracks/artists/albums/playlists |
| `spotify_now_playing` | Current track, artist, album, progress |
| `spotify_play` | Start/resume playback (optional context URI and device) |
| `spotify_pause` | Pause playback |
| `spotify_next` | Skip to next track |
| `spotify_previous` | Skip to previous track |
| `spotify_set_volume` | Set volume 0-100 |
| `spotify_queue` | Add a track to the queue |
| `spotify_list_playlists` | List your playlists |
| `spotify_playlist_tracks` | List tracks in a playlist |
| `spotify_create_playlist` | Create a playlist |
| `spotify_list_devices` | List available devices |
| `spotify_saved_tracks` | List your saved (liked) tracks |
| `spotify_transfer_playback` | Move playback to a device |

If the `SPOTIFY_*` variables are not set, tools return an error dict instead of raising.

## Notes

- Controlling playback requires an active Spotify device (open the Spotify app on phone/desktop/web).
- Tokens are cached in memory and refreshed automatically 60 seconds before expiry.
