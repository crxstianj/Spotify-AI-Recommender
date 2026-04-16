# Spotify AI Recommender


## ¿Cómo funciona?

El sistema extrae canciones desde una playlist de Spotify y las almacena en MongoDB. A partir de esos datos, entrena un modelo de similitud usando **TF-IDF** sobre atributos como géneros, artistas y álbum. Cuando el usuario selecciona una canción, se calculan las canciones más similares mediante **similitud coseno** y se muestran como recomendaciones.

<p align=center>
<img width="400" src="https://github.com/user-attachments/assets/311e6616-c7cc-4341-8b4c-471fb392e316" />
</p>

## Tecnologías

| Capa | Herramienta |
|------|-------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Base de datos | MongoDB |
| Modelo NLP | TF-IDF + Cosine Similarity (scikit-learn) |
| Contenerización | Docker / Docker Compose |
| Datos | Spotify Web API |

## Estructura del proyecto
```
├── backend/  
│   ├── model.py          # API FastAPI + lógica de recomendación  
│   ├── models/           # Modelos y matrices serializadas (.joblib)  
│   └── Dockerfile  
├── frontend/  
│   ├── front.py          # Interfaz Streamlit  
│   └── Dockerfile  
├── extraction.py         # Script de extracción de datos desde Spotify  
├── tokene.py             # Autenticación con Spotify  
└── docker-compose.yml
```
## Instalación y uso

### 1. Variables de entorno

Crea un archivo `.env` en la raíz con:
```env
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret

MONGO_USER=usuario
MONGO_PASS=contraseña
MONGO_HOST=mongo
MONGO_PORT=27017
DB_NAME=nombre_bd
COLLECTION_NAME=nombre_coleccion
```

### 2. Extraer datos

Ejecuta el script de extracción para poblar la base de datos:
```bash
python extraction.py
```

### 3. Levantar con Docker
```bash
docker-compose up --build
```

- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/songs` | Lista todas las canciones |
| `POST` | `/recomendar` | Devuelve recomendaciones para una canción |

**Ejemplo de request:**
```json
POST /recomendar
{ "nombre": "Blinding Lights" }
```
