import pandas as pd
from fastapi import FastAPI, HTTPException
import os
import pickle

# Inicializamos la aplicación
app = FastAPI()

# Ruta a los archivos de datos de la carpeta 'data'
BASE_DIR = os.path.join(os.path.dirname(__file__), "../data")

# Cargamos los datos
try:
    movies_df = pd.read_csv(os.path.join(BASE_DIR, "movies_transformed.csv"))
    credits_df = pd.read_csv(os.path.join(BASE_DIR, "credits.csv"))
    
    # Eliminar espacios de los nombres de las columnas
    movies_df.columns = movies_df.columns.str.strip()
    credits_df.columns = credits_df.columns.str.strip()
    
    # Crear la columna release_month a partir de la fecha de lanzamiento
    movies_df['release_date'] = pd.to_datetime(movies_df['release_date'], errors='coerce')
    movies_df['release_month'] = movies_df['release_date'].dt.month

    # Cargar matriz de similitud y títulos
    similarity_path = os.path.join(BASE_DIR, "cosine_similarity.pkl")
    titles_indices_path = os.path.join(BASE_DIR, "titles_indices.pkl")
    with open(similarity_path, "rb") as sim_file:
        cosine_sim = pickle.load(sim_file)
    with open(titles_indices_path, "rb") as indices_file:
        titles_indices = pickle.load(indices_file)

except FileNotFoundError as e:
    raise FileNotFoundError(f"Error al cargar los archivos: {e}")
except Exception as e:
    raise RuntimeError(f"Error inesperado: {e}")


# Endpoint para verificar nombres de columnas
@app.get("/debug/columnas")
def debug_columnas():
    try:
        return {"columnas": movies_df.columns.tolist()}
    except Exception as e:
        return {"error": str(e)}


# Otros endpoints (previamente existentes)


# Endpoint de recomendación
@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    try:
        # Verificar si el título existe en los datos
        if titulo not in titles_indices:
            raise HTTPException(status_code=404, detail=f"Película '{titulo}' no encontrada en el dataset.")
        
        # Obtener el índice de la película ingresada
        idx = titles_indices[titulo]
        
        # Obtener puntuaciones de similitud para esa película
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Ordenar las películas por similitud en orden descendente
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Obtener los índices de las 5 películas más similares (excluyendo la misma)
        sim_indices = [i[0] for i in sim_scores[1:6]]
        
        # Obtener los títulos de las películas similares
        recomendaciones = movies_df.iloc[sim_indices]["title"].tolist()
        
        return {"recomendaciones": recomendaciones}
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"error": str(e)}
