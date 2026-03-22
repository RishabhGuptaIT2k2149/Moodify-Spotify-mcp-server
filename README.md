# 🎵 moodify — mood to playlist MCP server

> describe your mood in plain english. get a spotify playlist back.

![Python](https://img.shields.io/badge/python-3.10+-1DB954?style=flat-square&logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-anthropic-purple?style=flat-square)
![Flask](https://img.shields.io/badge/flask-3.x-black?style=flat-square&logo=flask)
![Spotify](https://img.shields.io/badge/spotify-web%20API-1DB954?style=flat-square&logo=spotify&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

---

## what it does

you type something like *"I'm feeling nostalgic on a rainy Sunday afternoon"* — and moodify:

1. analyzes your mood using keyword mapping
2. translates it into spotify-friendly search terms (artist names, genres, descriptors)
3. queries the spotify API via a custom MCP tool
4. returns a curated tracklist with direct spotify links
5. renders everything in a dark, animated web UI

the core idea: **claude doesn't call spotify directly**. it calls *your* MCP tool, which calls spotify. that's the architectural pattern that makes this interesting.

---

## demo

```
you  →  "nostalgic rainy sunday, bittersweet and slow"
         ↓
claude  →  reasons about mood, picks tools
         ↓
MCP server  →  search_tracks("bon iver sufjan stevens acoustic indie folk")
         ↓
spotify API  →  returns 10 matching tracks
         ↓
web UI  →  animated track cards with open links
```

---

## architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   web frontend  │  HTTP   │   flask backend  │  async  │   spotify API   │
│   (index.html)  │ ──────► │    (app.py)      │ ──────► │  /v1/search     │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                              mood analysis
                              (MOOD_MAP logic)
                                     │
                             ┌───────▼────────┐
                             │   spotify.py   │
                             │  OAuth + httpx │
                             └────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   MCP server (server.py)                 │
│   tool: get_mood_playlist                               │
│   transport: stdio → Claude Desktop                     │
└─────────────────────────────────────────────────────────┘
```

two ways to use it:
- **web UI** — flask backend + `index.html` in browser
- **Claude Desktop** — connect `server.py` as an MCP server and chat directly

---

## tech stack

| layer | technology |
|---|---|
| MCP server | Python, `mcp` SDK (Anthropic) |
| HTTP client | `httpx` (async) |
| backend | Flask + Flask-CORS |
| frontend | vanilla HTML/CSS/JS |
| music data | Spotify Web API (OAuth 2.0) |
| auth | OAuth 2.0 Authorization Code + refresh token |

---

## project structure

```
mood-playlist-mcp/
├── server.py          # MCP server — tool definitions, stdio transport
├── spotify.py         # Spotify API client — auth, search
├── app.py             # Flask backend — mood analysis, REST endpoints
├── auth.py            # One-time OAuth utility — run once to get refresh token
├── index.html         # Web frontend
├── .env               # Secrets (never committed)
├── .gitignore
└── requirements.txt
```

---

## getting started

### prerequisites

- Python 3.10+
- A Spotify account (free or premium)
- A Spotify developer app ([developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))

### 1. clone and set up environment

```bash
git clone https://github.com/YOUR_USERNAME/mood-playlist-mcp.git
cd mood-playlist-mcp

python3 -m venv venv
source venv/bin/activate          # windows: venv\Scripts\activate

pip install mcp httpx python-dotenv flask anthropic flask-cors
```

### 2. create your spotify app

1. go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. click **create app**
3. set redirect URI to `http://127.0.0.1:8888/callback`
4. check **web API** under APIs used
5. copy your **client ID** and **client secret**

### 3. get your refresh token

open `auth.py` and fill in your credentials at the top:

```python
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
```

then run it once:

```bash
python3 auth.py
```

a browser window opens, you log in and approve, and your refresh token is printed in the terminal.

### 4. configure .env

create a `.env` file in the project root:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REFRESH_TOKEN=your_refresh_token
SPOTIFY_USER_ID=your_spotify_user_id
```

your spotify user ID is in your profile URL: `open.spotify.com/user/YOUR_ID_HERE`

### 5. run the web UI

```bash
python3 app.py
```

open `index.html` in your browser. type a mood, hit generate.

### 6. connect to claude desktop (optional)

edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mood-playlist": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "SPOTIFY_CLIENT_ID": "...",
        "SPOTIFY_CLIENT_SECRET": "...",
        "SPOTIFY_REFRESH_TOKEN": "...",
        "SPOTIFY_USER_ID": "..."
      }
    }
  }
}
```

restart Claude Desktop. you'll see a hammer icon — type your mood and claude will call your tool directly.

---

## mood mapping

the mood engine maps natural language to spotify search terms:

| mood keywords | search terms | vibe |
|---|---|---|
| nostalgic, rainy, sunday | bon iver, sufjan stevens, iron wine | low energy, acoustic |
| happy, sunny, upbeat | pharrell williams, jack johnson | high energy, pop |
| sad, heartbreak, lonely | elliott smith, phoebe bridgers | slow, minimal |
| focus, study, coding | brian eno, explosions in the sky | ambient, instrumental |
| workout, gym, hype | kendrick lamar, trap, edm | high energy, electronic |
| chill, relax, evening | lofi, nujabes, tame impala | mellow, lofi |
| romantic, love, tender | frank ocean, rex orange county | r&b, soul |

each mood category has 5 rotating search queries so you get different results on every generate.

---

## real world limitations i hit (and worked around)

this project ran into two spotify API restrictions in quick succession:

**spotify recommendations endpoint deprecated (2024)**
the `/recommendations` endpoint — which took audio features like `valence` and `energy` and returned matching tracks — was quietly deprecated. had to pivot to the `/search` endpoint with smarter, artist/genre-based queries instead of numeric audio parameters.

**playlist creation restricted (february 2026)**
spotify locked `playlist-modify-public` and `playlist-modify-private` for development mode apps as part of their new platform security changes. auto-creating playlists via the API is no longer possible without extended quota mode approval.

the workaround: return a curated tracklist with direct spotify links instead. users can add tracks to their own playlists manually. the core value — mood → music — still works.

this is just what building with third party APIs looks like right now. things deprecate, policies change, you adapt.

---

## what i'd build next

- swap hardcoded mood mapping for a claude API call — let the model handle the nuance
- last.fm API integration as a spotify fallback
- playlist export via spotify's new share links
- user accounts to save mood history
- browser extension version

---

## built by

rishabh — backend engineer learning to build with AI

this was a sunday project. one day from zero to working MCP server + web UI.

[linkedin](https://linkedin.com/in/YOUR_PROFILE) · [github](https://github.com/YOUR_USERNAME)

---

## license

MIT — do whatever you want with it.
