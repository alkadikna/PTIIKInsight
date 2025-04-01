from fastapi import FastAPI, BackgroundTasks
import subprocess
import pandas as pd
import os

app = FastAPI()

data_file = "../data/cleaned_data_api.csv"

@app.post("/scrape")
def run_scraping(background_tasks: BackgroundTasks):
    """Menjalankan proses scraping secara asynchronous."""
    def scrape():
        subprocess.run(["python", "../preprocessing/scraping.py"], check=True)
        subprocess.run(["python", "../preprocessing/preprocessing.py"], check=True)
        print("Scraping selesai dan data telah diproses.")
    
    background_tasks.add_task(scrape)
    return {"message": "Scraping sedang berjalan"}

@app.get("/data")
def get_scraped_data():
    """Mengembalikan hasil scraping yang sudah diproses."""
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        return df.to_dict(orient="records")
    return {"message": "Data belum tersedia, silakan jalankan scraping."}
