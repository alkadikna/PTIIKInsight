import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from tqdm import tqdm

# Load data
df = pd.read_csv('../data/cleaned_data.csv')
texts = df['Judul'].tolist()

# Create a CountVectorizer with Indonesian stop words
vectorizer_model = CountVectorizer()

# Model a.k.a BERTopic
topic_model = BERTopic(vectorizer_model=vectorizer_model, language="multilingual")  
topics, probabilities = topic_model.fit_transform(tqdm(texts, desc="Fitting BERTopic model"))

# Save the model
with open("bertopic_model_multi.pkl", "wb") as file:
    pickle.dump(topic_model, file)
df['topics'] = topics
df['probabilities'] = probabilities
df.to_csv('topic_modeling_results_multi.csv', index=False)