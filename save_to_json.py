from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import json

# PRIVATE CLIENT DATA LOAD
load_dotenv()

# Adatok megadása a Spotify API hozzáféréshez
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = Spotify(client_credentials_manager=credentials)

# Országok, amikhez keresünk később playlisteket
countries = {
    'US': 'United States', 'UK': 'United Kingdom', 'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 
    'ES': 'Spain', 'PL': 'Poland', 'SE': 'Sweden', 'NL': 'Netherlands', 'BE': 'Belgium', 
    'RU': 'Russia', 'BR': 'Brazil', 'IN': 'India', 'AU': 'Australia', 'JP': 'Japan', 
    'MX': 'Mexico', 'AR': 'Argentina', 'KR': 'South Korea', 'CA': 'Canada', 'HU': 'Hungary'
} # természetesen bővíthető, az egyszerűség kedvéért hússzal dolgozunk

# Függvény, ami visszaadja egy ország playlistjének azonosítóját
def get_playlist_id(country_name):
    query = f"Top 50 {country_name}"
    result = spotify.search(q=query, type='playlist', limit=1)
    
    # Ha találunk playlistet, akkor visszaadjuk az azonosítóját
    if result['playlists']['items']:
        return result['playlists']['items'][0]['id']
    else:
        print(f"No playlist found for country: {country_name}")
        return None

# Dictionary, amiben tároljuk az országokhoz tartozó playlistek azonosítóit ideiglenesen
playlist_ids = {}

# Végigmegyünk az országokon, és lekérjük a playlistek azonosítóit
for country_code, country_name in countries.items():
    playlist_id = get_playlist_id(country_name)
    if playlist_id:
        playlist_ids[country_code] = playlist_id

# Az országokhoz tartozó playlistek azonosítóit elmentjük egy JSON fájlba
with open('playlists.json', 'w') as f:
    json.dump(playlist_ids, f, indent=4)

print("Playlist IDs saved to 'playlists.json'.")
