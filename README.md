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
/PTIIKInsight  
│── data  
│────│── cleaned_data.csv  
│────│── raw_data.csv  
│  
│── Data-collection-preprocessing  
│────│── preprocessing.py  
│────│── scraping_data.py  
│  
│── Model-evaluation  
│────│── evaluation.ipynb  
│  
│── Model-training  
│────│── download_model.txt  
│────│── topic_modeling_results.csv  
│────│── train.py  
│  
│── README.md  

## Tools
Tools yang digunakan dalam projek ini:
- **Scraping Data** menggunakan [crawl4ai](https://github.com/unclecode/crawl4ai)
- **Preprocessing** menggunakan RegEx, nltk
- **Model** menggunakan BERTopic (percobaan menggunakan CountVectorizer dan embedded model seperti allenai-specter, paraphrase-multilingual-MiniLM-L12-v2, LaBSE, dan indoBERT)
