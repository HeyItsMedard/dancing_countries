from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import pandas as pd
import json

# PRIVATE CLIENT DATA LOAD
load_dotenv()

# Adatok megadása a Spotify API hozzáféréshez
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = Spotify(client_credentials_manager=credentials)

# Playlist azonosítók beolvasása JSON fájlból
with open('playlists.json', 'r') as f:
    playlist_ids = json.load(f)
    # Ha a JSON fájl nem létezik, akkor először futtassuk le a save_to_json.py-t
    if not os.path.exists('playlists.json'):
        os.system('python save_to_json.py')

# A top számok lekérdezése egy ország kód alapján
def get_top_tracks(country_code):
    playlist_id = playlist_ids.get(country_code)

    # Ha nem találjuk az ország kódhoz tartozó playlistet, váratlan működés - érdemes újra lekérni a playlisteket save_to_json.py futtatásával
    if not playlist_id:
        raise ValueError(f"No playlist found for country code: {country_code}")
    
    results = spotify.playlist_tracks(playlist_id, limit=50) 
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append({
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'id': track['id']
        })
    return tracks

# A számok audio jellemzőinek lekérdezése (táncolhatóság)
def get_audio_features(track_ids):
    features = spotify.audio_features(track_ids)
    return [{'id': f['id'], 'danceability': f['danceability']} for f in features if f]

# Egy előadó műfajainak lekérdezése
def get_artist_genres(artist_name):
    # Az első találatot vesszük, ha van
    artist_info = spotify.search(q=artist_name, type='artist', limit=1)
    if artist_info['artists']['items']:
        return artist_info['artists']['items'][0]['genres']
    else:
        return []

# Egy ország számait elemző függvény
def analyze_country_tracks(country_code):
    # Számok lekérdezése
    tracks = get_top_tracks(country_code)
    track_ids = [track['id'] for track in tracks]
    audio_features = get_audio_features(track_ids)
    
    # Átlagos táncolhatóság kiszámítása
    danceability_scores = [feature['danceability'] for feature in audio_features]
    avg_danceability = sum(danceability_scores) / len(danceability_scores) if danceability_scores else 0
    
    # Műfajok lekérdezése az előadók alapján
    all_genres = []
    for track in tracks:
        for artist_name in track['artists']:
            genres = get_artist_genres(artist_name)
            all_genres.extend(genres)
    
    # A leggyakoribb műfajok kiválasztása
    genre_counts = pd.Series(all_genres).value_counts().head(5).index.tolist()
    
    return {'country_code': country_code, 'avg_danceability': avg_danceability, 'top_genres': genre_counts}

# Eredmények kiírása TXT fájlba
def write_results_to_txt(results, filename="country_analysis.txt"):
    # Eredmények rendezése táncolhatóság alapján
    sorted_results = sorted(results, key=lambda x: x['avg_danceability'], reverse=True)
    
    with open(filename, "w") as f:
        f.write("Country Analysis (Top 5 Genres & Danceability)\n")
        f.write("=" * 50 + "\n")
        
        # Eredmények kiírása
        for idx, result in enumerate(sorted_results, start=1):
            f.write(f"\nCountry: {result['country_code']}\n")
            f.write(f"Placement: {idx}\n")  # Write placement number
            f.write(f"Average Danceability: {result['avg_danceability'] * 100:.2f}%\n")
            f.write("Top 5 Genres:\n")
            for i, genre in enumerate(result['top_genres'], start=1):
                f.write(f"  - {i}. {genre}\n")
            f.write("=" * 50 + "\n")

            import matplotlib.pyplot as plt

            # Függvény, ami létrehoz egy oszlopdiagramot a táncolhatóság alapján
            def create_danceability_chart(results, filename="dancers.png"):
                # Eredmények rendezése táncolhatóság alapján
                sorted_results = sorted(results, key=lambda x: x['avg_danceability'], reverse=True)
                
                # Adatok előkészítése
                country_codes = [result['country_code'] for result in sorted_results]
                danceability_scores = [result['avg_danceability'] for result in sorted_results]
                plt.xticks([])
                
                # Oszlopdiagram létrehozása
                plt.figure(figsize=(10, 8))
                bars = plt.barh(country_codes, danceability_scores, color='skyblue')
                
                # Magyarország piros színnel
                for bar, country_code in zip(bars, country_codes):
                    if country_code == 'HU':
                        bar.set_color('red')
                
                plt.xlabel('Average Danceability')
                plt.ylabel('Country Code')
                plt.title('Countries by Danceability')
                plt.gca().invert_yaxis()  # A legmagasabb érték legyen felül
                plt.tight_layout()
                
                # Diagram mentése fájlba
                plt.savefig(filename)
                plt.close()

            # Diagram létrehozása
            create_danceability_chart(results)

def main():
    countries = list(playlist_ids.keys())  # bekérés a playlist_ids-ből
    results = []
    
    # Időmérés
    # import time
    # start_time = time.time()

    # Végigmegyünk az országokon, és elemzünk minden ország számait
    for country in countries:
        try:
            result = analyze_country_tracks(country)
            results.append(result)
        except ValueError as e:
            print(f"Error for {country}: {e}")
    
    # Időmérés leállítása
    # end_time = time.time()
    # print(f"Analysis completed in {end_time - start_time:.2f} seconds.")

    # Kiiratás
    write_results_to_txt(results)

if __name__ == "__main__":
    main()
