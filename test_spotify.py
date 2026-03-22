import asyncio
from spotify import SpotifyClient

async def test():
    client = SpotifyClient()
    print("Searching for nostalgic rainy sunday tracks...\n")
    tracks = await client.search_tracks("genre:indie genre:folk acoustic melancholic", limit=10)
    for i, t in enumerate(tracks, 1):
        print(f"{i}. {t['name']} — {t['artist']}")
        print(f"   {t['url']}\n")

asyncio.run(test())