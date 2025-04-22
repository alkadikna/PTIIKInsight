import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pickle
import json
import mlflow
import mlflow.sklearn
from tqdm import tqdm
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
import nltk
from nltk.tokenize import word_tokenize

# Set experiment MLflow
mlflow.set_experiment("BERTopic-Text-Modeling")

# Load data JSON
with open("../data/cleaned_data_v3.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert ke DataFrame
df = pd.DataFrame(data)
df['Abstrak'] = df['Abstrak'].fillna('')
df['combined_text'] = df['Judul'] + ". " + df['Abstrak']
texts = df['combined_text'].tolist()

# Konfigurasi eksperimen
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
language = "multilingual"
topic_min_size = 10

if __name__ == "__main__":
    nltk.download('punkt')
    # Mulai tracking di MLflow
    with mlflow.start_run(run_name=f"BERTopic-{embedding_model_name.split('/')[-1]}") as run:
        mlflow.log_param("embedding_model", embedding_model_name)
        mlflow.log_param("language", language)
        mlflow.log_param("min_topic_size", topic_min_size)

        embedding_model = SentenceTransformer(embedding_model_name, device="cuda")
        topic_model = BERTopic(
            embedding_model=embedding_model,
            language=language,
            min_topic_size=topic_min_size
        )

        topics, probabilities = topic_model.fit_transform(tqdm(texts, desc="Training BERTopic"))

        tokenized_texts = [word_tokenize(text.lower()) for text in texts]
        dictionary = Dictionary(tokenized_texts)
        corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

        topics_words = [
            [word for word, _ in topic_model.get_topic(topic_id)]
            for topic_id in range(len(set(topics)) - (1 if -1 in topics else 0))
        ]

        coherence_model = CoherenceModel(
            topics=topics_words,
            texts=tokenized_texts,
            corpus=corpus,
            dictionary=dictionary,
            coherence='c_v'
        )
        coherence_score = coherence_model.get_coherence()
        mlflow.log_metric("coherence_score", coherence_score)

        model_path = "bertopic_model_minilm.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(topic_model, f)
        mlflow.log_artifact(model_path)

        df['topics'] = topics
        df['probabilities'] = probabilities
        result_path = 'topic_modeling_results_minilm.csv'
        df.to_csv(result_path, index=False)
        mlflow.log_artifact(result_path)

    print("Eksperimen selesai & logged di MLflow.")

