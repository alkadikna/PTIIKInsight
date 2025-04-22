import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import os
import json

nltk.download('stopwords')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_PATH = os.path.join(BASE_DIR, "../data/data_raw_v3.json") 
TARGET_PATH = os.path.join(BASE_DIR, "../data/cleaned_data_v3.json") 

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\d]', '', text) 
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip() 
    stops = set(stopwords.words('indonesian'))
    tokens = text.split()
    tokens = [word for word in tokens if word not in stops]
    return ' '.join(tokens)

def remove_first_word(title: str) -> str:
    words = title.split()
    return ' '.join(words[1:]) if len(words) > 1 else ''

with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Preprocessing
df['Judul'] = df['Judul'].apply(clean_text)
df['Judul'] = df['Judul'].apply(remove_first_word)
df['Abstrak'] = df['Abstrak'].apply(clean_text)

# Delete noise, duplicates, and irrelevant data
df = df[~df['Judul'].str.lower().str.contains('halaman sampul')]
df = df.drop_duplicates(subset=['Judul'])
df = df.drop(columns=['Issue ID'])

# Save to JSON
df.to_json(TARGET_PATH, orient='records', indent=4, force_ascii=False)
print("Saved to", TARGET_PATH)
