# backend/Dockerfile
FROM python:3.12-slim

# Requisitos del sistema (si usas pandas/scikit-learn conviene tener estas libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Code Engine inyecta PORT, usa 8080 por defecto
ENV PORT=8080 \
    PYTHONUNBUFFERED=1

# Arranque con gunicorn (ajusta módulo si tu app se llama distinto)
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:${PORT}", "app:app"]
