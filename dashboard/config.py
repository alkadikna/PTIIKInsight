# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

# Monitoring Configuration
GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"

# Dashboard Configuration
DASHBOARD_TITLE = "PTIIK Insight Dashboard"
DASHBOARD_ICON = "🔬"
DASHBOARD_LAYOUT = "wide"

# File Paths (relative to project root)
MODEL_PATH = "model/bertopic_model_all-MiniLM-min20.pkl"
DATA_PATH = "data/cleaned/cleaned_data.csv"
SCRAPING_SCRIPT = "preprocessing/scraping.py"
PREPROCESSING_SCRIPT = "preprocessing/preprocessing.py"
TRAINING_SCRIPT = "model/train.py"

# Prediction Configuration
MAX_PREDICTION_BATCH_SIZE = 100
PREDICTION_TIMEOUT = 60

# Training Configuration
TRAINING_TIMEOUT = 1800  # 30 minutes
DEFAULT_MIN_TOPIC_SIZE = 20
AVAILABLE_EMBEDDING_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "intfloat/multilingual-e5-large-instruct"
]

# UI Configuration
SIDEBAR_WIDTH = 300
CHART_HEIGHT = 400
TABLE_HEIGHT = 300

# Status Check Configuration
SERVICE_CHECK_TIMEOUT = 5
HEALTH_CHECK_INTERVAL = 30

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
