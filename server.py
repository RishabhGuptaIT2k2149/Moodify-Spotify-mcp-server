import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from spotify import SpotifyClient

mcp = Server("mood-playlist")
spotify = SpotifyClient()

@mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_mood_playlist",
            description="""Searches Spotify for tracks that match a mood or vibe.
            IMPORTANT: The 'genres' parameter should contain Spotify-friendly search terms like
            artist names, genres, and descriptive words — NOT the mood itself.
            For example:
            - Mood 'nostalgic rainy sunday' → genres='indie folk acoustic bon iver sufjan stevens'
            - Mood 'pumped up workout' → genres='hip hop trap edm high energy'
            - Mood 'happy summer road trip' → genres='pop rock indie upbeat arcade fire'
            - Mood 'sad late night' → genres='ambient piano slowcore elliot smith'
            - Mood 'focused deep work' → genres='instrumental post-rock ambient brian eno'
            Always populate the genres field with music search terms that will find the right sound on Spotify.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "description": "Natural language mood or vibe description e.g. 'nostalgic and melancholic rainy day'"
                    },
                    "genres": {
                        "type": "string",
                        "description": "Spotify-friendly search terms — artist names, genres, descriptive words. e.g. 'bon iver indie folk acoustic sufjan stevens'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of tracks to return, default 15",
                        "default": 15
                    }
                },
                "required": ["mood", "genres"]
            }
        )
    ]

@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_mood_playlist":
        mood = arguments.get("mood", "")
        genres = arguments.get("genres", "")
        limit = arguments.get("limit", 15)

        try:
            # Search using the Spotify-friendly genre/artist terms
            tracks = await spotify.search_tracks(genres, limit=limit)

            if not tracks:
                return [types.TextContent(type="text", text="No tracks found for that mood.")]

            lines = [f"Found {len(tracks)} tracks for: *{mood}*\n"]
            for i, t in enumerate(tracks, 1):
                lines.append(f"{i}. {t['name']} — {t['artist']} | {t['url']}")

            return [types.TextContent(type="text", text="\n".join(lines))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as (read, write):
        await mcp.run(read, write, mcp.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())