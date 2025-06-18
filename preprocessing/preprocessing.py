import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import os
import json

nltk.download('stopwords')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_PATH = os.path.join(BASE_DIR, "../data/data_raw_v4.json") 
TARGET_PATH = os.path.join(BASE_DIR, "../data/cleaned_data_v4.json") 

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

# Check if DataFrame is empty or missing required columns
if df.empty:
    print("Warning: DataFrame is empty")
    exit(0)

if 'title' not in df.columns:
    print(f"Error: 'title' column not found. Available columns: {df.columns.tolist()}")
    exit(1)

print(f"Processing {len(df)} records...")

# Delete noise
df = df[~df['title'].str.lower().str.contains('halaman sampul', na=False)]

# Preprocessing
df['title'] = df['title'].apply(clean_text)
df['title'] = df['title'].apply(remove_first_word)

# Only process abstract if it exists
if 'abstract' in df.columns:
    df['abstract'] = df['abstract'].apply(clean_text)
else:
    print("Warning: 'abstract' column not found, skipping abstract processing")

# Delete duplicates, and irrelevant data
df = df.drop_duplicates(subset=['title'])

# Drop issue ID column if it exists
if 'issue ID' in df.columns:
    df = df.drop(columns=['issue ID'])

print(f"Processed data saved with {len(df)} records")

# Save to JSON
df.to_json(TARGET_PATH, orient='records', indent=4, force_ascii=False)
print("Saved to", TARGET_PATH)
