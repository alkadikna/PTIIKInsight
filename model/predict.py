import joblib
import pandas as pd

MODEL_PATH = "model/bertopic_model_all-MiniLM-min20.pkl"

model = joblib.load(MODEL_PATH)

def predict_topic(texts: list[str]) -> list[str]:
    """
    Menerima list of text, kembalikan list of predicted topics.
    """
    df = pd.DataFrame({'text': texts})
    # Kamu bisa menambahkan preprocessing di sini kalau perlu
    preds = model.predict(df['text'])
    return preds.tolist()
