import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import pickle
from tqdm import tqdm

# Load data
df = pd.read_csv('../data/cleaned_data.csv')
texts = df['Judul'].tolist()

# Load paraphrase-multilingual-MiniLM-L12-v2 dengan CUDA
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cuda")

# Buat BERTopic dengan model embedding
topic_model = BERTopic(embedding_model=embedding_model, language="multilingual")  
topics, probabilities = topic_model.fit_transform(tqdm(texts, desc="Fitting BERTopic model"))

# Save the model
with open("bertopic_model.pkl", "wb") as file:
    pickle.dump(topic_model, file)
df['topics'] = topics
df['probabilities'] = probabilities
df.to_csv('topic_modeling_results.csv', index=False)