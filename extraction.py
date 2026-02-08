import os
import requests
from dotenv import load_dotenv
from tokene import SpotifyAuth
from pymongo import MongoClient
from urllib.parse import quote_plus

# === CARGAR VARIABLES DE ENTORNO ===
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
auth = SpotifyAuth(client_id, client_secret)

# === OBTENER AUTORIZACIÓN ===
headers = auth.get_auth_header()

# === OBTENER TODOS LOS TRACKS DEL PLAYLIST===
playlist_id = "7apTmCm2QNVPm21HA5Zm9f"
url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
all_items = []

while url:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    all_items.extend(data["items"])
    url = data.get("next")

# === PROCESAR TRACKS ===
track_data = []
artist_id_map = {}

# Obtener IDs únicos de artistas principales
artist_ids = set()
for item in all_items:
    track = item.get("track")
    if not track:
        continue
    if track["artists"]:
        artist_ids.add(track["artists"][0]["id"])

# === OBTENER GÉNEROS EN BATCH ===
artist_ids = list(artist_ids)
for i in range(0, len(artist_ids), 50):
    batch_ids = artist_ids[i:i+50]
    artist_url = f"https://api.spotify.com/v1/artists?ids={','.join(batch_ids)}"
    try:
        res = requests.get(artist_url, headers=headers)
        res.raise_for_status()
        artists_data = res.json().get("artists", [])
        for artist in artists_data:
            artist_id_map[artist["id"]] = artist.get("genres", [])
    except Exception as e:
        print(f"Error al obtener géneros: {e}")

# === CONSTRUIR LOS DATOS DE TRACKS ===
for item in all_items:
    track = item.get("track")
    if not track:
        continue

    artist = track["artists"][0]
    artist_id = artist["id"]
    genres = artist_id_map.get(artist_id, [])

    track_data.append({
        "id": track["id"],
        "nombre": track["name"],
        "artistas": ", ".join(a["name"] for a in track["artists"]),
        "album": track["album"]["name"],
        "fecha_lanzamiento": track["album"]["release_date"],
        "popularidad": track["popularity"],
        "explicit": track["explicit"],
        "imagen_url": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
        "spotify_url": track["external_urls"]["spotify"],
        "generos": ", ".join(genres)
    })

# === GUARDAR EN MONGODB ===
usuario = quote_plus(os.getenv("MONGO_USER"))
passw = quote_plus(os.getenv("MONGO_PASS"))
host = os.getenv("MONGO_HOST")
puerto = os.getenv("MONGO_PORT")
mongo_uri = f"mongodb://{usuario}:{passw}@{host}:{puerto}/"
client = MongoClient(mongo_uri)
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]
if track_data:
    collection.insert_many(track_data)
    print(f"Datos guardados en MongoDB en la colección 'tracks'")
else:
    print("No hay datos para guardar en MongoDB.")
