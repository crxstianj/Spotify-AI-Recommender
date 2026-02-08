# Imagen base con Python
FROM python:3.11-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar librerías del sistema necesarias para scikit-learn y pymongo
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*


# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install \
    fastapi \
    "uvicorn[standard]" \
    pandas \
    python-dotenv \
    scikit-learn \
    joblib \
    pymongo \
    pydantic

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la app
CMD ["uvicorn", "model:app", "--host", "0.0.0.0", "--port", "8000"]
