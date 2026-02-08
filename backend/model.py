from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from dotenv import load_dotenv
from urllib.parse import quote_plus
from pymongo import MongoClient
#load_dotenv
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Conexión a MongoDB ---
usuario = quote_plus(os.getenv("MONGO_USER"))
passw = quote_plus(os.getenv("MONGO_PASS"))
host = os.getenv("MONGO_HOST")
puerto = os.getenv("MONGO_PORT")
mongo_uri = f"mongodb://{usuario}:{passw}@{host}:{puerto}/"
client = MongoClient(mongo_uri)
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]


df = None
vectorizer = None
tfidf_matrix = None
similitud = None

def train():
    global df, vectorizer, tfidf_matrix, similitud

    archivos = [
        'models/playlist_contenido.csv',
        'models/modelo_vectorizer.joblib',
        'models/tfidf_matrix.joblib',
        'models/similitud_matrix.joblib'
    ]

    if all(os.path.exists(f) for f in archivos):
        print("Cargando modelo y matrices desde disco...")
        df = pd.read_csv('models/playlist_contenido.csv')
        vectorizer = joblib.load('models/modelo_vectorizer.joblib')
        tfidf_matrix = joblib.load('models/tfidf_matrix.joblib')
        similitud = joblib.load('models/similitud_matrix.joblib')
    else:
        print("Entrenando modelo y calculando matrices desde MongoDB...")

        # === Cargar datos desde MongoDB ===
        documentos = list(collection.find({}, {
            "_id": 0,
            "nombre": 1,
            "artistas": 1,
            "album": 1,
            "fecha_lanzamiento": 1,
            "explicit": 1,
            "imagen_url": 1,
            "generos": 1,
            "popularidad": 1,
            "spotify_url": 1
        }))
        df = pd.DataFrame(documentos)

        # Preprocesar y entrenar modelo
        df['generos'] = df['generos'].fillna('')

        def combinar_info(row):
            return f"{row['generos']} {row['artistas']} {row['album']} {row['explicit']}"

        df['contenido'] = df.apply(combinar_info, axis=1)

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df['contenido'])
        similitud = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Guardar para futuras ejecuciones
        df.to_csv('models/playlist_contenido.csv', index=False)
        joblib.dump(vectorizer, 'models/modelo_vectorizer.joblib')
        joblib.dump(tfidf_matrix, 'models/tfidf_matrix.joblib')
        joblib.dump(similitud, 'models/similitud_matrix.joblib')


train()

class Cancion(BaseModel):
    nombre: str

def recomendar(nombre_cancion: str, top_n=5):
    nombre_cancion = nombre_cancion.lower()
    indices = df[df['nombre'].str.lower() == nombre_cancion].index
    if len(indices) == 0:
        return []
    idx = indices[0]
    similitudes = list(enumerate(similitud[idx]))
    # Excluir la canción original explícitamente
    similitudes = [(i, score) for i, score in similitudes if i != idx]
    similitudes = sorted(similitudes, key=lambda x: x[1], reverse=True)[:top_n]
    recomendados = [i[0] for i in similitudes]
    return df.iloc[recomendados][['nombre', 'artistas', 'album', 'generos', 'fecha_lanzamiento', 'popularidad', 'spotify_url', 'imagen_url']].to_dict(orient='records')


@app.post("/recomendar")
def obtener_recomendaciones(cancion: Cancion):
    resultados = recomendar(cancion.nombre)
    if not resultados:
        raise HTTPException(status_code=404, detail="Canción no encontrada.")

    print(resultados)
    return {"recomendaciones": resultados}

from fastapi.responses import JSONResponse

@app.get("/songs")
def obtener_canciones():
    try:
        canciones = list(collection.find({}, {
            "_id": 0,
            "nombre": 1,
            "artistas": 1,
            "album": 1,
            "generos": 1,
            "popularidad": 1,
            "spotify_url": 1,
            "imagen_url": 1,
            "fecha_lanzamiento": 1
        }))


        canciones_adaptadas = [
            {
                "title": c.get("nombre"),
                "artist": c.get("artistas"),
                "album": c.get("album"),
                "genre": c.get("generos"),
                "year": c.get("fecha_lanzamiento"),
                "spotify_url": c.get("spotify_url"),
                "image_url": c.get("imagen_url")
            }
            for c in canciones
        ]

        return JSONResponse(content=canciones_adaptadas)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener canciones: {str(e)}")
