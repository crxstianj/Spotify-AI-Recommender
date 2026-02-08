import streamlit as st
import requests
import random
from PIL import Image
import io

# Configuración de la página
st.set_page_config(
    page_title="Sistema de recomendaciones",
    page_icon="🎵",
    layout="wide"
)
#LOCAL
#API_BASE_URL = "http://localhost:8000"

#DOCKER
API_BASE_URL = "http://backend:8000"


@st.cache_data(ttl=300)
def get_all_songs():
    try:
        response = requests.get(f"{API_BASE_URL}/songs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al obtener canciones: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return []

def get_random_songs(songs, count=5):
    return random.sample(songs, count) if len(songs) > count else songs

def get_recommendations(song_title):
    try:
        response = requests.post(f"{API_BASE_URL}/recomendar", json={"nombre": song_title})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al obtener recomendaciones: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión al obtener recomendaciones: {e}")
        return []

def display_song_card(song):
    col1, col2 = st.columns([1, 3])

    with col1:
        if 'image_url' in song and song['image_url']:
            try:
                response = requests.get(song['image_url'])
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, width=150)
                else:
                    st.image("https://via.placeholder.com/150x150?text=No+Image", width=150)
            except:
                st.image("https://via.placeholder.com/150x150?text=No+Image", width=150)
        else:
            st.image("https://via.placeholder.com/150x150?text=No+Image", width=150)

    with col2:
        st.subheader(song.get('title', 'Título desconocido'))
        st.write(f"**Artista:** {song.get('artist', 'Artista desconocido')}")
        st.write(f"**Álbum:** {song.get('album', 'Álbum desconocido')}")

        if 'duration' in song:
            duration_seconds = song['duration']
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            st.write(f"**Duración:** {minutes:02d}:{seconds:02d}")

        if 'genre' in song:
            st.write(f"**Género:** {song['genre']}")

        if 'year' in song:
            st.write(f"**Año:** {song['year']}")

        if 'spotify_url' in song and song['spotify_url']:
            try:
                spotify_id = song['spotify_url'].split("/")[-1].split("?")[0]
                embed_url = f"https://open.spotify.com/embed/track/{spotify_id}"
                st.markdown(
                    f"""
                    <iframe src="{embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.warning(f"No se pudo cargar el reproductor de Spotify: {e}")

# Estado inicial
if 'random_songs' not in st.session_state:
    st.session_state.random_songs = []
if 'all_songs' not in st.session_state:
    st.session_state.all_songs = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = ''

# Cargar canciones si no se han cargado aún
if not st.session_state.all_songs:
    with st.spinner("Cargando canciones..."):
        st.session_state.all_songs = get_all_songs()
        st.session_state.random_songs = get_random_songs(st.session_state.all_songs)

# Título principal
st.title("Music Recommender")
st.markdown("---")

# Sección superior: canciones aleatorias
col1, col2 = st.columns([3, 1])

with col1:
    st.header("Canciones Aleatorias")

with col2:
    if st.button("Actualizar canciones aleatorias"):
        st.session_state.random_songs = get_random_songs(st.session_state.all_songs)
        st.success("Canciones actualizadas")

# Mostrar canciones aleatorias y botones de recomendación
for i, song in enumerate(st.session_state.random_songs):
    with st.container():
        display_song_card(song)
        # Botón de recomendaciones
        if st.button("Ver recomendaciones", key=f"rec_btn_{song['title']}"):
            st.session_state.recommendations = get_recommendations(song['title'])
            st.session_state.selected_title = song['title']
        if i < len(st.session_state.random_songs) - 1:
            st.markdown("---")

# Mostrar recomendaciones (después de canciones aleatorias)
if st.session_state.recommendations:
    st.markdown("---")
    st.subheader(f"Recomendaciones basadas en: {st.session_state.selected_title}")

    for rec in st.session_state['recommendations']['recomendaciones']:
        with st.container():
            display_song_card({
                'title': rec.get('nombre'),
                'artist': rec.get('artistas'),
                'album': rec.get('album'),
                'genre': ', '.join(rec.get('generos', [])) if isinstance(rec.get('generos'), list) else rec.get('generos', ''),
                'year': rec.get('fecha_lanzamiento'),
                'image_url': rec.get('imagen_url'),
                'spotify_url': rec.get('spotify_url', '')
            })
            st.markdown("---")
