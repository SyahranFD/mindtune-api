import os
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
client_id = os.getenv("SP_CLIENT_ID")
client_secret = os.getenv("SP_CLIENT_SECRET")
redirect_uri = os.getenv("SP_REDIRECT_URI")
scope = os.getenv("SP_SCOPE")
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=CacheFileHandler(cache_path=".spotify_cache"),
    show_dialog=True,
)