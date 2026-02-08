# Imagen base oficial de Python
FROM python:3.11-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos del frontend
COPY . /app

# Instalar dependencias del sistema necesarias para Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install \
    streamlit \
    requests \
    pillow

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "front.py", "--server.port=8501", "--server.address=0.0.0.0"]
