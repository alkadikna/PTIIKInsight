import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer

df = pd.read_csv('../data/cleaned_data_nofirstword.csv')

# Model embedding
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Buat embedding untuk setiap judul
df['Embedding'] = df['Judul'].apply(lambda x: model.encode(x).tolist())

# Save
with open('../data/embedded_titles.pkl', 'wb') as f:
    pickle.dump(df, f)

print("Embedding berhasil disimpan!")
