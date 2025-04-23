import json
import pickle
import nltk
import os
import tempfile
import pandas as pd
import mlflow
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from nltk.tokenize import word_tokenize
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel


def main():
    # Load data
    with open("../data/cleaned_data_v3.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df['Abstrak'] = df['Abstrak'].fillna('')
    df['combined_text'] = df['Judul'] + ". " + df['Abstrak']
    texts = df['combined_text'].tolist()
    tokenized_texts = [word_tokenize(text.lower()) for text in texts]
    dictionary = Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

    # Model configs
    embedding_models = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "intfloat/multilingual-e5-large-instruct"
    ]
    min_topic_size = 10

    # Set MLflow experiment
    mlflow.set_experiment("BERTopic-Model Embedding Experiment")

    # Gridsearch
    for embedding_model_name in embedding_models:
        with mlflow.start_run(run_name=f"{embedding_model_name.split('/')[-1]}-min{min_topic_size}"):
            mlflow.log_param("embedding_model", embedding_model_name)
            mlflow.log_param("min_topic_size", min_topic_size)

            embedding_model = SentenceTransformer(embedding_model_name, device="cuda")
            topic_model = BERTopic(
                embedding_model=embedding_model,
                language="multilingual",
                min_topic_size=min_topic_size,
                calculate_probabilities=True
            )

            topics, probs = topic_model.fit_transform(tqdm(texts, desc="Training BERTopic"))

            # Coherenfce
            topic_words = [
                [word for word, _ in topic_model.get_topic(topic_id)]
                for topic_id in range(len(set(topics)) - (1 if -1 in topics else 0))
            ]
            coherence_model = CoherenceModel(
                topics=topic_words,
                texts=tokenized_texts,
                corpus=corpus,
                dictionary=dictionary,
                coherence='c_v'
            )
            coherence_score = coherence_model.get_coherence()
            mlflow.log_metric("coherence_score", coherence_score)
            mlflow.log_metric("num_topics", len(set(topics)) - (1 if -1 in topics else 0))

            with tempfile.TemporaryDirectory() as tmpdir:
                # Simpan model
                model_path = os.path.join(tmpdir, f"bertopic_model_{embedding_model_name.split('/')[-1]}_{min_topic_size}.pkl")
                with open(model_path, "wb") as f:
                    pickle.dump(topic_model, f)
                mlflow.log_artifact(model_path)

                # Simpan hasil topik
                df['topics'] = topics
                df['probabilities'] = [list(p) for p in probs]

                result_path = os.path.join(tmpdir, f"topic_results_{embedding_model_name.split('/')[-1]}_{min_topic_size}.csv")
                df.to_csv(result_path, index=False)
                mlflow.log_artifact(result_path)

if __name__ == "__main__":
    nltk.download("punkt")
    main()
