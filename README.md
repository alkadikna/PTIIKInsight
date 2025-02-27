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
Data berasal dari arsip [jurnal PTIIK Universitas Brawijaya](https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/archive)

## Struktur Repositori
📁 TopicModelingJPTIIK_MLOps  
├── 📁 Data-collection-preprocessing > Berisi source code untuk data collecting dan preprocessing  
├── 📁 Model-training > Source code training model  
├── 📁 Model-evaluation > Source code model evaluation  
├── 📁 Data > Data hasil scraping dan preprocessing  
├── 📄 README.md  

## Tools
Tools yang digunakan dalam projek ini:
- **Scraping Data** menggunakan [crawl4ai](https://github.com/unclecode/crawl4ai)
- **Preprocessing** menggunakan RegEx, nltk
- **Model** menggunakan BERTopic (percobaan menggunakan CountVectorizer dan embedded model seperti allenai-specter, paraphrase-multilingual-MiniLM-L12-v2, LaBSE, dan indoBERT)
