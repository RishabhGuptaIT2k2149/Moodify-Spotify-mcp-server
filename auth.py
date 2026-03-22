import httpx
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

CLIENT_ID = "f04d2145d14f49fea33adcbb099eb30c"
CLIENT_SECRET = "1c60700e67c24e38b79dc8fa958a9332"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"
auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Got it! You can close this tab.")

    def log_message(self, format, *args):
        pass  # silence server logs

def get_refresh_token():
    # 1. Open Spotify login in browser
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    })

    # 2. Start local server to catch the callback
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening Spotify login in your browser...")
    webbrowser.open(auth_url)
    thread.join()

    if not auth_code:
        print("Failed to get auth code")
        return

    # 3. Exchange code for tokens
    response = httpx.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    tokens = response.json()

    if "refresh_token" not in tokens:
        print("Error:", tokens)
        return

    print("\n✅ Success!")
    print(f"Refresh token: {tokens['refresh_token']}")
    print("\nCopy this into your .env file as SPOTIFY_REFRESH_TOKEN=...")

if __name__ == "__main__":
    get_refresh_token()