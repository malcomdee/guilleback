# backend/Dockerfile
FROM python:3.12-slim

# Requisitos del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# No usamos PORT dinámico, seteamos directamente
ENV PYTHONUNBUFFERED=1

# Exponemos puerto fijo
EXPOSE 8000

# Arranque con gunicorn en puerto fijo
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8000", "app:app"]
