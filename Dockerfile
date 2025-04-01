# Use base image with Python 3.10
FROM python:3.10

# Set working directory in container
WORKDIR /app

# Install dependencies
COPY ../requirements.txt .

RUN pip install -r requirements.txt

# Copy all file
COPY . .

# Run FastAPI using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
