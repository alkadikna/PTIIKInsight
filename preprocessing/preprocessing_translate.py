import pandas as pd
import re
import nltk
import torch
from nltk.corpus import stopwords
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

nltk.download('stopwords')

device = "cuda" if torch.cuda.is_available() else "cpu"

model_name = "facebook/m2m100_418M"
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name).to(device)

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

def translate_to_english(text: str) -> str:
    tokenizer.src_lang = "id"
    encoded_text = tokenizer(text, return_tensors="pt").to(device)
    output = model.generate(**encoded_text, forced_bos_token_id=tokenizer.get_lang_id("en"))
    translated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return translated_text

df = pd.read_csv('../data/raw_data.csv')

df['Judul'] = df['Judul'].apply(clean_title)

df = df[~df['Judul'].str.lower().str.contains('halaman sampul')]

df['Judul'] = df['Judul'].apply(remove_first_word)

df = df.drop_duplicates(subset=['Judul'])

df = df.drop(columns=['Issue ID'])

df['Judul'] = df['Judul'].apply(translate_to_english)

df.to_csv('../data/cleaned_data_nofirstword_eng.csv', index=False)

print("saved to data/cleaned_dat_nofirstword_eng.csv")