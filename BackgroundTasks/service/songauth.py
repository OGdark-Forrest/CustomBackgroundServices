from utils import general
from utils.imports import *

CLIENT_ID = "0907d0d611a2466797facf3d7c907fdd" 
CLIENT_SECRET = "6edd571d95734f09ba1c732993209d78" 
REDIRECT_URI = "http://127.0.0.1:3000"

AUTH_CODE = None
tokenFile = general.pathInfo("jsonAuth")+"spotify_tokens.json"

class SpotifyCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE

        # Get query parameters from redirect URL
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            AUTH_CODE = params["code"][0]

            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"Authorization successful! You can close this window."
            )

        elif "error" in params:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                b"Authorization denied."
            )

        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                b"No authorization code found."
            )

def set_spotify_playback_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI):

    scope = "user-modify-playback-state user-read-playback-state"

    auth_url = "https://accounts.spotify.com/authorize"

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope
    }

    full_auth_url = auth_url + "?" + urlencode(params)

    server = HTTPServer(("localhost", 3000), SpotifyCallbackHandler)

    webbrowser.open(full_auth_url)

    server.handle_request()

    if AUTH_CODE is None:
        raise Exception("Authorization failed.")

    token_url = "https://accounts.spotify.com/api/token"

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("ascii")
    encoded_auth = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "redirect_uri": redirect_uri
    }

    response = requests.post(
        token_url,
        headers=headers,
        data=data
    )

    if response.status_code != 200:
        raise Exception(
            f"Token request failed: {response.status_code}\n{response.text}"
        )

    token_data = response.json()

    token_data["expires_at"] = time.time() + token_data["expires_in"]

    general.writeJSON(tokenFile, token_data)

def refresh_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    tokenData = general.readJSON(tokenFile)

    refresh_token = tokenData["refresh_token"]
    token_url = "https://accounts.spotify.com/api/token"

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("ascii")
    encoded_auth = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(
        token_url,
        headers=headers,
        data=data
    )

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    token_data["expires_at"] = time.time() + token_data["expires_in"]

    # preserve refresh token if Spotify doesn't return a new one
    if "refresh_token" not in token_data:
        token_data["refresh_token"] = refresh_token

    general.writeJSON(tokenFile, token_data)

def token_valid():
    if os.path.exists(tokenFile):
        with open(tokenFile) as rfile:
            token_data = json.load(rfile)
    else:
        return {"valid": False, "created": False}
    if time.time() < token_data["expires_at"]:
        return {"valid": True, "created": True, "expired": False, "accessToken": token_data["access_token"]}
    else:
        return {"valid": False, "created": True, "expired": True}