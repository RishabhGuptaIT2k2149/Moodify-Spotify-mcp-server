import asyncio
import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from spotify import SpotifyClient

load_dotenv()

app = Flask(__name__)
CORS(app)
spotify = SpotifyClient()

MOOD_MAP = [
    {
        "keywords": ["nostalgic", "memories", "past", "reminisce", "bittersweet", "rainy", "sunday", "slow", "grey", "gray"],
        "queries": [
            "bon iver acoustic indie folk",
            "sufjan stevens melancholic",
            "iron wine singer songwriter",
            "nick drake folk acoustic",
            "the national sad indie",
        ],
        "energy": "low", "tempo": "slow", "sound": "acoustic", "mood": "nostalgic, melancholic, warm"
    },
    {
        "keywords": ["happy", "joy", "excited", "cheerful", "good vibes", "sunny", "upbeat", "positive"],
        "queries": [
            "pharrell williams happy pop",
            "upbeat feel good indie pop",
            "vampire weekend sunny",
            "foster the people upbeat",
            "jack johnson feel good",
        ],
        "energy": "high", "tempo": "fast", "sound": "pop", "mood": "happy, upbeat, bright"
    },
    {
        "keywords": ["sad", "depressed", "heartbreak", "lonely", "cry", "grief", "loss", "hurt"],
        "queries": [
            "elliott smith sad acoustic",
            "phoebe bridgers grief folk",
            "lana del rey melancholic",
            "radical face emotional",
            "passenger heartbreak acoustic",
        ],
        "energy": "low", "tempo": "slow", "sound": "minimal", "mood": "sad, lonely, quiet"
    },
    {
        "keywords": ["focus", "work", "study", "concentrate", "productive", "deep", "coding"],
        "queries": [
            "brian eno ambient instrumental",
            "explosions in the sky post rock",
            "tycho electronic ambient",
            "bonobo instrumental chill",
            "four tet electronic ambient",
        ],
        "energy": "medium", "tempo": "medium", "sound": "instrumental", "mood": "focused, calm, deep"
    },
    {
        "keywords": ["workout", "gym", "pump", "energy", "run", "hype", "intense", "motivated"],
        "queries": [
            "kanye west hip hop energy",
            "kendrick lamar hype rap",
            "eminem workout intense",
            "trap hip hop high energy",
            "edm electronic pump up",
        ],
        "energy": "high", "tempo": "fast", "sound": "electronic", "mood": "pumped, intense, driven"
    },
    {
        "keywords": ["chill", "relax", "lounge", "evening", "calm", "peaceful", "quiet", "wind down"],
        "queries": [
            "lofi hip hop jazzy beats",
            "nujabes jazz hop chill",
            "tame impala psychedelic chill",
            "air french electronic chill",
            "zero 7 downtempo lounge",
        ],
        "energy": "low", "tempo": "slow", "sound": "lofi", "mood": "chill, relaxed, mellow"
    },
    {
        "keywords": ["party", "dance", "night out", "club", "fun", "friends", "celebration"],
        "queries": [
            "daft punk dance electronic",
            "disco funk dance floor",
            "house music electronic dance",
            "calvin harris dance pop",
            "the weeknd night out",
        ],
        "energy": "high", "tempo": "fast", "sound": "electronic", "mood": "festive, energetic, fun"
    },
    {
        "keywords": ["romantic", "love", "date", "intimate", "tender", "sweet", "crush"],
        "queries": [
            "frank ocean romantic r&b",
            "rex orange county love",
            "daniel caesar soul r&b",
            "mac miller tender",
            "still woozy indie romance",
        ],
        "energy": "medium", "tempo": "slow", "sound": "r&b", "mood": "romantic, tender, warm"
    },
    {
        "keywords": ["angry", "frustrated", "rage", "mad", "vent", "stress", "tense"],
        "queries": [
            "nirvana grunge rock",
            "radiohead alternative rock",
            "rage against the machine",
            "nine inch nails industrial",
            "arctic monkeys rock intense",
        ],
        "energy": "high", "tempo": "fast", "sound": "rock", "mood": "intense, raw, cathartic"
    },
    {
        "keywords": ["morning", "wake up", "coffee", "fresh", "start", "new day", "sunrise"],
        "queries": [
            "jack johnson morning acoustic",
            "ben harper light folk",
            "fleet foxes morning folk",
            "the lumineers acoustic morning",
            "gregory alan isakov gentle folk",
        ],
        "energy": "medium", "tempo": "medium", "sound": "acoustic", "mood": "fresh, gentle, hopeful"
    },
]

DEFAULT_QUERIES = [
    "indie alternative pop",
    "alternative rock classic",
    "singer songwriter acoustic",
    "electronic ambient chill",
    "soul r&b classic",
]

def analyze_mood(mood_text: str) -> dict:
    mood_lower = mood_text.lower()
    scores = []
    for m in MOOD_MAP:
        score = sum(1 for kw in m["keywords"] if kw in mood_lower)
        scores.append(score)

    best = max(range(len(scores)), key=lambda i: scores[i])

    if scores[best] == 0:
        return {
            "genres": random.choice(DEFAULT_QUERIES),
            "energy": "medium", "tempo": "medium",
            "sound": "mixed", "moodLabel": "eclectic, varied"
        }

    matched = MOOD_MAP[best]
    return {
        "genres": random.choice(matched["queries"]),
        "energy": matched["energy"],
        "tempo": matched["tempo"],
        "sound": matched["sound"],
        "moodLabel": matched["mood"]
    }

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    mood = data.get("mood", "")
    if not mood:
        return jsonify({"error": "No mood provided"}), 400
    return jsonify(analyze_mood(mood))

@app.route("/playlist", methods=["POST"])
def get_playlist():
    data = request.json
    mood = data.get("mood", "")
    genres = data.get("genres", "")

    if not mood and not genres:
        return jsonify({"error": "No mood provided"}), 400

    analysis = analyze_mood(mood)
    query = genres if genres else analysis["genres"]

    try:
        tracks = asyncio.run(spotify.search_tracks(query, limit=10))
        random.shuffle(tracks)
        return jsonify({
            "mood": mood,
            "analysis": analysis,
            "tracks": tracks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
