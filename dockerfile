# Usa una imagen base de Python
FROM python:3.12-slim

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor y lo instala
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido necesario del proyecto al contenedor
COPY ./scripts /app/scripts
COPY ./data /app/data

# Exponer el puerto que usará FastAPI
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "scripts.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
