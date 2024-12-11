from fastapi import FastAPI
import pandas as pd
import glob
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from fastapi.middleware.cors import CORSMiddleware

# Habilitar CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar los datos transformados
try:
    movies_files = glob.glob("data/transformed/transformed_movies/*.csv")
    credits_files = glob.glob("data/transformed/transformed_credits/*.csv")

    if movies_files:
        movies = pd.concat(
            (pd.read_csv(f, quotechar='"', on_bad_lines='skip') for f in movies_files),
            ignore_index=True
        )
        movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
        logger.info("Datos de películas cargados correctamente.")
    else:
        movies = pd.DataFrame()
        logger.warning("No se encontraron datos de películas.")

    if credits_files:
        credits = pd.concat(
            (pd.read_csv(f, quotechar='"', on_bad_lines='skip') for f in credits_files),
            ignore_index=True
        )
        logger.info("Datos de créditos cargados correctamente.")
    else:
        credits = pd.DataFrame()
        logger.warning("No se encontraron datos de créditos.")
except Exception as e:
    logger.error(f"Error al cargar los datos: {e}")
    movies = pd.DataFrame()
    credits = pd.DataFrame()

# Endpoint raíz
@app.get("/")
def root():
    return {"message": "API está funcionando correctamente"}

# Endpoint: Cantidad de filmaciones por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
        "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
        "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    mes_numero = meses.get(mes.lower())
    if not mes_numero:
        return {"error": "Mes no válido"}
    count = movies[movies['release_date'].dt.month == mes_numero].shape[0]
    return {"mes": mes, "cantidad": count}

# Endpoint: Cantidad de filmaciones por día
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    dias = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6
    }
    dia_numero = dias.get(dia.lower())
    if dia_numero is None:
        return {"error": "Día no válido"}
    count = movies[movies['release_date'].dt.dayofweek == dia_numero].shape[0]
    return {"dia": dia, "cantidad": count}

# Endpoint: Score de una película por título
@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    movie = movies[movies['title'].str.lower() == titulo.lower()]
    if movie.empty:
        return {"error": "Película no encontrada"}
    return {
        "titulo": titulo,
        "anio": int(movie['release_year'].values[0]),
        "score": float(movie['popularity'].values[0])
    }

# Endpoint: Votos de una película por título
@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    movie = movies[movies['title'].str.lower() == titulo.lower()]
    if movie.empty:
        return {"error": "Película no encontrada"}
    if int(movie['vote_count'].values[0]) < 2000:
        return {"mensaje": "La película no tiene suficientes votos para este análisis"}
    return {
        "titulo": titulo,
        "votos_totales": int(movie['vote_count'].values[0]),
        "promedio_votos": float(movie['vote_average'].values[0])
    }

# Endpoint: Información de un actor
@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    try:
        actor_data = credits[credits['cast'].str.contains(nombre_actor, na=False, case=False)]
        if actor_data.empty:
            return {"error": f"No se encontraron películas para el actor {nombre_actor}"}

        retorno_total = actor_data['return'].sum()
        cantidad_peliculas = actor_data.shape[0]
        promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0

        return {
            "actor": nombre_actor,
            "cantidad_peliculas": cantidad_peliculas,
            "retorno_total": retorno_total,
            "promedio_retorno": promedio_retorno
        }
    except Exception as e:
        return {"error": f"Error procesando la solicitud: {str(e)}"}

# Endpoint: Información de un director
@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    try:
        director_data = credits[credits['crew'].str.contains(nombre_director, na=False, case=False)]
        if director_data.empty:
            return {"error": f"No se encontraron películas para el director {nombre_director}"}

        resultados = []
        for _, row in director_data.iterrows():
            resultados.append({
                "titulo": row['title'],
                "fecha_lanzamiento": row['release_date'],
                "retorno": row['return'],
                "costo": row['budget'],
                "ganancia": row['revenue']
            })

        return {
            "director": nombre_director,
            "peliculas": resultados
        }
    except Exception as e:
        return {"error": f"Error procesando la solicitud: {str(e)}"}

# Endpoint: Recomendación de películas
@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    if 'overview' not in movies.columns:
        return {"error": "La columna 'overview' no está disponible para generar recomendaciones"}

    # Verificar si la película existe
    movie = movies[movies['title'].str.lower() == titulo.lower()]
    if movie.empty:
        return {"error": "Película no encontrada"}

    # Crear la matriz TF-IDF basada en la sinopsis (overview)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['overview'].fillna(''))

    # Calcular similitud de coseno
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Obtener índice de la película consultada
    idx = movie.index[0]

    # Obtener puntuaciones de similitud
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Seleccionar las 5 películas más similares (excluyendo la misma película)
    similar_movies = [
        movies.iloc[i]['title'] for i, score in similarity_scores[1:6]
    ]

    return {"titulo_consultado": titulo, "recomendaciones": similar_movies}
