import httpx
import time
import os
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        self._access_token = None
        self._token_expiry = 0

    async def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._token_expiry - 60:
            return self._access_token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(self.client_id, self.client_secret)
            )
            tokens = response.json()
            if "access_token" not in tokens:
                raise Exception(f"Token refresh failed: {tokens}")
            self._access_token = tokens["access_token"]
            self._token_expiry = time.time() + tokens["expires_in"]
            return self._access_token

    async def search_tracks(self, query: str, limit: int = 10) -> list[dict]:
        token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "q": query,
                    "type": "track",
                    "limit": 10,
                    "market": "IN"
                }
            )
            data = response.json()
            if "tracks" not in data:
                raise Exception(f"Search failed: {data}")
            return [
                {
                    "name": t["name"],
                    "artist": t["artists"][0]["name"],
                    "album": t["album"]["name"],
                    "url": t["external_urls"]["spotify"],
                    "preview_url": t.get("preview_url")
                }
                for t in data["tracks"]["items"]
            ]
