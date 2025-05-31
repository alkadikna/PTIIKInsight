from fastapi import FastAPI, BackgroundTasks
from prometheus_fastapi_instrumentator import Instrumentator
import subprocess
import pandas as pd
import os
from model.predict import predict_topic
from pydantic import BaseModel

app = FastAPI()
Instrumentator().instrument(app).expose(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "../data/cleaned_data.csv") 
SCRAPING_PATH = os.path.join(BASE_DIR, "../preprocessing/scraping.py") 
PREPROCESSING_PATH = os.path.join(BASE_DIR, "../preprocessing/preprocessing.py") 

@app.post("/scrape")
def run_scraping(background_tasks: BackgroundTasks):
    """Menjalankan proses scraping secara asynchronous."""
    def scrape():
        subprocess.run(["python", SCRAPING_PATH], check=True)
        subprocess.run(["python", PREPROCESSING_PATH], check=True)
        print("Scraping selesai dan data telah diproses.")
    
    background_tasks.add_task(scrape)
    return {"message": "Scraping sedang berjalan"}

@app.get("/data")
def get_scraped_data():
    """Mengembalikan hasil scraping yang sudah diproses."""
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        return df.to_dict(orient="records")
    return {"message": "Data belum tersedia, silakan jalankan scraping."}

class PredictRequest(BaseModel):
    texts: list[str]

@app.post("/predict")
def predict(req: PredictRequest):
    """Endpoint untuk prediksi topik dari teks."""
    result = predict_topic(req.texts)
    return {"topics": result}

class PredictRequest(BaseModel):
    texts: list[str]

@app.post("/predict")
def predict(req: PredictRequest):
    """Endpoint untuk prediksi topik dari teks."""
    result = predict_topic(req.texts)
    return {"topics": result}