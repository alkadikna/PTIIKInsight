from fastapi import FastAPI, BackgroundTasks, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import subprocess
import pandas as pd
import os
import time
import logging
from model.predict import predict_topic
from pydantic import BaseModel
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PTIIK Insight API", description="ML-powered topic analysis for research papers")

# Initialize Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Custom metrics
model_predictions_total = Counter('model_predictions_total', 'Total number of model predictions')
model_prediction_errors_total = Counter('model_prediction_errors_total', 'Total number of model prediction errors')
model_prediction_duration = Histogram('model_prediction_duration_seconds', 'Time spent on model predictions')
model_accuracy = Gauge('model_accuracy', 'Current model accuracy')
scraping_requests_total = Counter('scraping_requests_total', 'Total number of scraping requests')
scraping_errors_total = Counter('scraping_errors_total', 'Total number of scraping errors')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "../data/cleaned_data.csv") 
SCRAPING_PATH = os.path.join(BASE_DIR, "../preprocessing/scraping.py") 
PREPROCESSING_PATH = os.path.join(BASE_DIR, "../preprocessing/preprocessing.py")

@app.post("/scrape")
def run_scraping(background_tasks: BackgroundTasks):
    """Menjalankan proses scraping secara asynchronous."""
    scraping_requests_total.inc()
    
    def scrape():
        try:
            logger.info("Starting scraping process...")
            subprocess.run(["python", SCRAPING_PATH], check=True)
            subprocess.run(["python", PREPROCESSING_PATH], check=True)
            logger.info("Scraping completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Scraping failed: {e}")
            scraping_errors_total.inc()
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
            scraping_errors_total.inc()
    
    background_tasks.add_task(scrape)
    return {"message": "Scraping sedang berjalan", "status": "started"}

@app.get("/data")
def get_scraped_data():
    """Mengembalikan hasil scraping yang sudah diproses."""
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            logger.info(f"Data retrieved successfully, {len(df)} records")
            return {
                "message": "Data retrieved successfully",
                "count": len(df),
                "data": df.to_dict(orient="records")
            }
        else:
            logger.warning("Data file not found")
            return {"message": "Data belum tersedia, silakan jalankan scraping.", "status": "no_data"}
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving data")

class PredictRequest(BaseModel):
    texts: List[str]

@app.post("/predict")
def predict(req: PredictRequest):
    """Endpoint untuk prediksi topik dari teks."""
    start_time = time.time()
    
    try:
        # Validate input
        if not req.texts:
            raise HTTPException(status_code=400, detail="Empty text list provided")
        
        if len(req.texts) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Too many texts provided (max 100)")
        
        # Make prediction
        result = predict_topic(req.texts)
        model_predictions_total.inc()
        
        # Record prediction time
        prediction_time = time.time() - start_time
        model_prediction_duration.observe(prediction_time)
        
        logger.info(f"Prediction completed for {len(req.texts)} texts in {prediction_time:.2f}s")
        
        return {
            "message": "Prediction completed successfully",
            "input_count": len(req.texts),
            "prediction_time": prediction_time,
            "topics": result
        }
        
    except Exception as e:
        model_prediction_errors_total.inc()
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "model_loaded": os.path.exists(os.path.join(BASE_DIR, "../model/bertopic_model_all-MiniLM-min20.pkl"))
    }

@app.post("/update-accuracy")
def update_model_accuracy(accuracy: float):
    """Update model accuracy metric (typically called after model evaluation)."""
    if 0 <= accuracy <= 1:
        model_accuracy.set(accuracy)
        logger.info(f"Model accuracy updated to {accuracy}")
        return {"message": "Model accuracy updated", "accuracy": accuracy}
    else:
        raise HTTPException(status_code=400, detail="Accuracy must be between 0 and 1")