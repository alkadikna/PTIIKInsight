# Gunakan image dasar dengan Python 3.10
FROM python:3.10

# Set working directory dalam container
WORKDIR /app

# Copy requirements.txt dan install dependencies
COPY api/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN crawl4ai-setup

COPY ../api ./api

COPY ../preprocessing ./preprocessing
# COPY ../data ./data
RUN mkdir -p /app/data

# Ekspose port 8000 agar bisa diakses dari Codespaces
EXPOSE 8000

# Jalankan FastAPI dengan Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]