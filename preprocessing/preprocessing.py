import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import os

nltk.download('stopwords')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_PATH = os.path.join(BASE_DIR, "../data/data_raw.csv") 
TARGET_PATH = os.path.join(BASE_DIR, "../data/cleaned_data.csv") 


def clean_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[\d]', '', title)
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    stops = set(stopwords.words('indonesian'))
    tokens = title.split()
    tokens = [word for word in tokens if word not in stops]
    return ' '.join(tokens)

def remove_first_word(title: str) -> str:
    words = title.split()
    return ' '.join(words[1:]) if len(words) > 1 else ''


df = pd.read_csv(SOURCE_PATH)

df['Judul'] = df['Judul'].apply(clean_title)

df = df[~df['Judul'].str.lower().str.contains('halaman sampul')]

df['Judul'] = df['Judul'].apply(remove_first_word)

df = df.drop_duplicates(subset=['Judul'])

df = df.drop(columns=['Issue ID'])


df.to_csv(TARGET_PATH, index=False)

print("saved to", TARGET_PATH)