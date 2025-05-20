import requests
import time

for _ in range(20):
    try:
        requests.get("http://localhost:8000/data")
        requests.post("http://localhost:8000/scrape")
        print("Request sent.")
    except Exception as e:
        print("Failed:", e)
    time.sleep(2)  # setiap 2 detik
