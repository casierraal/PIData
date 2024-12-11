FROM python:3.9-slim

# Actualizar el sistema base e instalar Java y dependencias
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Establecer la variable JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Descargar e instalar Apache Spark
RUN curl -fSL https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz -o spark-3.3.2-bin-hadoop3.tgz && \
    tar -xvf spark-3.3.2-bin-hadoop3.tgz && \
    mv spark-3.3.2-bin-hadoop3 /opt/spark && \
    rm spark-3.3.2-bin-hadoop3.tgz


# Establecer variables de entorno para Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Definir el directorio de trabajo
WORKDIR /app

# Copiar las dependencias e instalar librerías de Python
COPY requeriments.txt requeriments.txt
RUN pip install --no-cache-dir -r requeriments.txt

# Copiar el proyecto al contenedor
COPY . .

# Comando para ejecutar la API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
