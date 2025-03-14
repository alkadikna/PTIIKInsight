# ANALISIS TREN TOPIK PENELITIAN DALAM PUBLIKASI JURNAL PTIIK

<p align="center">
  <img src="https://github.com/user-attachments/assets/51ba4164-4edc-4c26-bdb2-e21cfbc94abd" alt="JPTIIK" height="200"/>
</p>

## Daftar Isi
- [Tim/Collaborator](#tim-gugugaga)
- [Sumber Data](#sumber-data)
- [Struktur Repositori](#struktur-repositori)
- [Tools](#tools)

## Tim GuguGaga
- Muhammad Rajendra Alkautsar Dikna [@alkadikna](http://github.com/alkadikna)
- Rochmanu Purnomohadi Erfitra [@nrcst](http://github.com/nrcst)
- I Kadek Surya Satya Dharma [@Suryy16](http://github.com/suryy16)

## Sumber Data
Data berasal dari arsip [Jurnal PTIIK Universitas Brawijaya](https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/archive)

## Struktur Repositori
```bash
/PTIIKInsight  
│  
├── data  
│   ├── cleaned_data_nofirstword.csv  
│   ├── cleaned_data.csv  
│   ├── data_raw_v2.csv  
│   ├── eda.ipynb  
│   ├── embedded_titles.pkl  
│   └── raw_data.csv  
│  
├── model  
│   ├── train.py  
│   └── evaluation  
│       └── evaluation.ipynb  
│  
├── preprocessing  
│   ├── embedding.py  
│   ├── preprocessing_translate.py  
│   ├── preprocessing.py  
│   └── scraping_data.py  
│  
├── README.md 
└── requirements.txt
```

## Tools
Tools yang digunakan dalam projek ini:
- **Scraping Data** menggunakan [crawl4ai](https://github.com/unclecode/crawl4ai)
- **Preprocessing** menggunakan RegEx, nltk
- **Model** menggunakan BERTopic (percobaan menggunakan CountVectorizer dan embedded model seperti allenai-specter, paraphrase-multilingual-MiniLM-L12-v2, LaBSE, dan indoBERT)

## Installation and Setup
Untuk menginstall seluruh dependencies, jalankan perintah:

```
pip install -r requirements.txt
```

Setelah itu, inisialisasi crawl4ai dengan langkah-langkah berikut:
```
# Install the package
pip install -U crawl4ai

# For pre release versions
pip install crawl4ai --pre

# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```