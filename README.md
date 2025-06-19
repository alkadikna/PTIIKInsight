# ANALISIS TREN TOPIK PENELITIAN DALAM PUBLIKASI JURNAL PTIIK

<p align="center">
  <img src="https://github.com/user-attachments/assets/51ba4164-4edc-4c26-bdb2-e21cfbc94abd" alt="JPTIIK" height="200"/>
</p>

## Daftar Isi
- [Tim/Collaborator](#tim-gugugaga)
- [Sumber Data](#sumber-data)
- [Struktur Repositori](#struktur-repositori)
- [Tools](#tools)
- [Monitoring Dashboard](#monitoring-dashboard)
- [Installation and Setup](#installation-and-setup)

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
- **API** menggunakan FastAPI dengan Uvicorn
- **Monitoring** menggunakan Prometheus dan Grafana
- **Dashboarding** menggunakan Streamlit
- **Containerization** menggunakan Docker dan Docker Compose

## Monitoring Dashboard

Proyek ini dilengkapi dengan dashboard monitoring komprehensif yang memantau:

### 📊 Metrics yang Dipantau
- **Model Performance**: Akurasi model, waktu prediksi, tingkat keberhasilan/kegagalan
- **API Performance**: Request rate, response time, error rate
- **Scraping Activity**: Status scraping, tingkat error
- **System Resources**: CPU, Memory usage

### 🎛️ Dashboard Access
Setelah menjalankan `docker-compose up`, akses:
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **API Documentation**: http://localhost:8000/docs

### 📈 Fitur Dashboard
- Real-time model accuracy tracking
- API performance monitoring
- Alerting untuk anomali performa
- Historical trend analysis
- Resource utilization monitoring

Lihat [Monitoring README](monitoring/README.md) untuk detail lengkap.

## Installation and Setup

### Quick Start dengan Docker (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd PTIIKInsight

# Start all services (API, Prometheus, Grafana)
docker-compose up -d

# Wait for services to initialize
sleep 30

# Generate test traffic for dashboard
python simulation.py

# Access services:
# - API: http://localhost:8000
# - Grafana: http://localhost:3000 (admin/admin)  
# - Prometheus: http://localhost:9090
```

### Manual Installation
Untuk menginstall seluruh dependencies, jalankan perintah:

```bash
pip install -r requirements.txt
```

Setelah itu, inisialisasi crawl4ai dengan langkah-langkah berikut:
```bash
# Install the package
pip install -U crawl4ai

# For pre release versions
pip install crawl4ai --pre

# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

### API Usage Examples
```bash
# Health check
curl http://localhost:8000/health

# Predict topics
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["machine learning algorithms", "web development"]}'

# Start scraping
curl -X POST "http://localhost:8000/scrape"

# Get scraped data
curl http://localhost:8000/data
```