import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


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


df = pd.read_csv('../data/data_raw_v2.csv')

df['Judul'] = df['Judul'].apply(clean_title)

df = df[~df['Judul'].str.lower().str.contains('halaman sampul')]

df['Judul'] = df['Judul'].apply(remove_first_word)

df = df.drop_duplicates(subset=['Judul'])

df = df.drop(columns=['Issue ID'])


df.to_csv('../data/cleaned_data.csv', index=False)

print("saved to data/cleaned_dat_nofirstword.csv")