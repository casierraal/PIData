from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, year
import os

def transform_data(input_movies, input_credits, output_dir):
    try:
        # Crear la sesión de Spark
        spark = SparkSession.builder \
            .appName("Movies Transformation") \
            .getOrCreate()

        print("Iniciando transformación de datos...")

        # Leer los datasets
        print(f"Leyendo archivos: {input_movies} y {input_credits}")
        movies = spark.read.csv(input_movies, header=True, inferSchema=True)
        credits = spark.read.csv(input_credits, header=True, inferSchema=True)

        # Transformaciones solicitadas
        movies = movies.fillna({'revenue': 0, 'budget': 0})  # Rellenar nulos en revenue y budget con 0
        movies = movies.dropna(subset=['release_date'])  # Eliminar filas sin fecha de lanzamiento
        movies = movies.withColumn("release_year", year(col("release_date")))  # Extraer año de release_date
        movies = movies.withColumn("return", when(col("budget") == 0, 0).otherwise(col("revenue") / col("budget")))  # Calcular retorno
        
        # Eliminar solo columnas no requeridas (manteniendo overview)
        print("Eliminando columnas no requeridas...")
        movies = movies.drop("video", "imdb_id", "adult", "original_title", "poster_path", "homepage")

        # Crear carpeta de salida si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Guardar los datos transformados
        print("Guardando datos transformados en el directorio de salida...")
        movies.write.csv(os.path.join(output_dir, "transformed_movies"), header=True, mode="overwrite")
        credits.write.csv(os.path.join(output_dir, "transformed_credits"), header=True, mode="overwrite")

        print("Transformaciones completadas y guardadas en:", output_dir)
    except Exception as e:
        print(f"Error durante la transformación: {e}")

if __name__ == "__main__":
    transform_data(
        input_movies="data/movies_dataset.csv",  # Ruta del archivo original de películas
        input_credits="data/credits.csv",       # Ruta del archivo original de créditos
        output_dir="data/transformed"           # Directorio de salida para los datos transformados
    )
