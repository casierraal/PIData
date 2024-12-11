import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Función para cargar un archivo CSV con manejo de errores
def load_csv_with_debug(filepath):
    print(f"Cargando archivo: {filepath}")
    try:
        data = pd.read_csv(filepath, on_bad_lines='skip', sep=',', low_memory=False)
        print(f"Archivo cargado exitosamente: {filepath}")
        print(f"Dimensiones del dataframe: {data.shape}")
        return data
    except Exception as e:
        print(f"Error al cargar el archivo {filepath}: {e}")
        return None

# Rutas a los archivos transformados
credits_path = "data/transformed/transformed_credits/part-00000-c389ee88-6e10-4437-8b36-ec936f44282d-c000.csv"
movies_path = "data/transformed/transformed_movies/part-00000-307bb76b-7c01-4a8b-9210-5b140a0dba46-c000.csv"

# Cargar datos
credits = load_csv_with_debug(credits_path)
movies = load_csv_with_debug(movies_path)

# Analizar y visualizar datos cargados
if movies is not None:
    # Convertir columnas a numéricas (reemplazando errores por NaN)
    movies['budget'] = pd.to_numeric(movies['budget'], errors='coerce')
    movies['revenue'] = pd.to_numeric(movies['revenue'], errors='coerce')

    # Gráfico de la distribución de presupuestos
    plt.figure(figsize=(10, 6))
    movies['budget'].dropna().plot(kind='hist', bins=50, title='Distribución de presupuestos')
    plt.xlabel('Presupuesto')
    plt.savefig('visualizations/budget_distribution.png')
    plt.close()

    # Gráfico de la distribución de ingresos
    plt.figure(figsize=(10, 6))
    movies['revenue'].dropna().plot(kind='hist', bins=50, title='Distribución de ingresos')
    plt.xlabel('Ingresos')
    plt.savefig('visualizations/revenue_distribution.png')
    plt.close()

    # Nube de palabras para títulos de películas
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(movies['title'].dropna()))
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nube de palabras: Títulos de películas')
    plt.savefig('visualizations/title_wordcloud.png')
    plt.close()

    print("Visualizaciones guardadas en la carpeta 'visualizations'.")

# Mostrar resumen de valores nulos
if movies is not None:
    print(f"Valores nulos en películas:\n{movies.isnull().sum()}")

if credits is not None:
    print(f"Valores nulos en créditos:\n{credits.isnull().sum()}")
