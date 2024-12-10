import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Ruta base en función del entorno (Docker o local)
base_path = os.environ.get("DATA_PATH", os.path.join(os.path.dirname(__file__), "../data"))

# Construir rutas absolutas para los archivos
credits_path = os.path.join(base_path, "credits.csv")
movies_path = os.path.join(base_path, "movies_dataset.csv")

# Cargar los datasets en DataFrames
try:
    credits_df = pd.read_csv(credits_path)
    movies_df = pd.read_csv(movies_path, low_memory=False)  # Evitar warnings por tipos mixtos
except FileNotFoundError as e:
    print(f"No se encontró el archivo: {e}")
    raise

# Transformaciones en movies_df
try:
    # 1. Rellenar valores nulos en revenue y budget con 0
    movies_df["revenue"] = pd.to_numeric(movies_df["revenue"], errors="coerce").fillna(0)
    movies_df["budget"] = pd.to_numeric(movies_df["budget"], errors="coerce").fillna(0)

    # 2. Eliminar valores nulos en release_date
    movies_df = movies_df.dropna(subset=["release_date"])

    # 3. Formatear fechas y crear columna release_year
    movies_df["release_date"] = pd.to_datetime(movies_df["release_date"], errors="coerce")
    movies_df["release_year"] = movies_df["release_date"].dt.year

    # 4. Crear la columna "return" (revenue / budget)
    movies_df["return"] = movies_df.apply(
        lambda row: row["revenue"] / row["budget"] if row["budget"] > 0 else 0, axis=1
    )

    # 5. Eliminar columnas no necesarias
    columns_to_drop = ["video", "imdb_id", "adult", "original_title", "poster_path", "homepage"]
    movies_df = movies_df.drop(columns=columns_to_drop)

    # Guardar los datos transformados
    output_path = os.path.join(base_path, "movies_transformed.csv")
    movies_df.to_csv(output_path, index=False)

    # Crear matriz de similitud para recomendaciones
    print("Generando matriz de similitud para el sistema de recomendación...")

    # Usar la columna 'overview' para calcular similitudes (asegúrate de que no tenga valores nulos)
    movies_df["overview"] = movies_df["overview"].fillna("")

    # Crear una matriz TF-IDF a partir de los resúmenes con filtros para evitar un tamaño de matriz muy grande
    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=10000,  # Limitar la cantidad de características a las más importantes
        min_df=5,  # Ignorar términos que aparecen en menos de 5 documentos
    )
    tfidf_matrix = tfidf.fit_transform(movies_df["overview"])

    # Calcular la similitud coseno entre todas las películas
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Guardar la matriz de similitud en un archivo
    similarity_path = os.path.join(base_path, "cosine_similarity.pkl")
    pd.to_pickle(cosine_sim, similarity_path)

    # Guardar el índice de películas
    titles_indices_path = os.path.join(base_path, "titles_indices.pkl")
    titles_indices = pd.Series(movies_df.index, index=movies_df["title"]).to_dict()
    pd.to_pickle(titles_indices, titles_indices_path)

    # Mensaje de éxito
    print(f"Transformación completada. Archivo transformado guardado como '{output_path}'.")
    print(f"Matriz de similitud guardada como '{similarity_path}'.")
    print(f"Índice de títulos guardado como '{titles_indices_path}'.")
except Exception as e:
    print(f"Se produjo un error en el procesamiento de los datos: {e}")
    raise

