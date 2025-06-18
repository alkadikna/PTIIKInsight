import streamlit as st
import requests
import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.config import *

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class APIClient:
    """Client for interacting with the PTIIK Insight API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = API_TIMEOUT
    
    def check_health(self) -> Tuple[bool, Optional[Dict]]:
        """Check if the API is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health", 
                timeout=SERVICE_CHECK_TIMEOUT
            )
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False, None
    
    def predict_topics(self, texts: List[str]) -> Tuple[bool, Any]:
        """Run topic prediction"""
        try:
            if len(texts) > MAX_PREDICTION_BATCH_SIZE:
                return False, f"Too many texts. Maximum allowed: {MAX_PREDICTION_BATCH_SIZE}"
            
            response = requests.post(
                f"{self.base_url}/predict",
                json={"texts": texts},
                timeout=PREDICTION_TIMEOUT
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return False, str(e)
    
    def start_scraping(self) -> Tuple[bool, Any]:
        """Start the scraping process"""
        try:
            response = requests.post(
                f"{self.base_url}/scrape",
                timeout=SERVICE_CHECK_TIMEOUT
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Scraping start failed: {e}")
            return False, str(e)
    
    def get_data(self) -> Tuple[bool, Any]:
        """Get scraped data"""
        try:
            response = requests.get(
                f"{self.base_url}/data",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            return False, str(e)
    
    def update_accuracy(self, accuracy: float) -> Tuple[bool, Any]:
        """Update model accuracy metric"""
        try:
            response = requests.post(
                f"{self.base_url}/update-accuracy",
                params={"accuracy": accuracy},
                timeout=SERVICE_CHECK_TIMEOUT
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Accuracy update failed: {e}")
            return False, str(e)

class ServiceMonitor:
    """Monitor external services"""
    
    def __init__(self):
        self.services = {
            "API": {"url": f"{API_BASE_URL}/health", "status": False},
            "Grafana": {"url": f"{GRAFANA_URL}/api/health", "status": False},
            "Prometheus": {"url": f"{PROMETHEUS_URL}/api/v1/query?query=up", "status": False}
        }
    
    def check_all_services(self) -> Dict[str, Dict]:
        """Check status of all services"""
        for service, config in self.services.items():
            try:
                response = requests.get(config["url"], timeout=SERVICE_CHECK_TIMEOUT)
                config["status"] = response.status_code == 200
                config["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                config["status"] = False
                config["error"] = str(e)
                config["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return self.services
    
    def get_health_percentage(self) -> float:
        """Get overall system health percentage"""
        total_services = len(self.services)
        online_services = sum(1 for s in self.services.values() if s["status"])
        return (online_services / total_services) * 100 if total_services > 0 else 0

class FileManager:
    """Manage file operations for the dashboard"""
    
    @staticmethod
    def get_project_root() -> str:
        """Get the project root directory"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_model_info() -> Dict[str, Any]:
        """Get information about the current model"""
        project_root = FileManager.get_project_root()
        model_path = os.path.join(project_root, MODEL_PATH)
        
        if os.path.exists(model_path):
            stats = os.stat(model_path)
            return {
                "exists": True,
                "size_mb": stats.st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(stats.st_mtime),
                "path": model_path
            }
        else:
            return {"exists": False, "path": model_path}
    
    @staticmethod
    def load_sample_data() -> List[str]:
        """Load sample texts for testing"""
        return [
            "machine learning algorithms for data analysis and pattern recognition",
            "deep neural networks and artificial intelligence applications",
            "web development using modern frameworks and best practices",
            "database optimization and performance tuning techniques",
            "cybersecurity threats and protection methods in digital systems",
            "cloud computing infrastructure and scalable services",
            "mobile application development for iOS and Android platforms",
            "data mining and knowledge discovery in large datasets",
            "computer vision and image processing algorithms",
            "natural language processing and text analytics applications"
        ]

class DataProcessor:
    """Process and format data for dashboard display"""
    
    @staticmethod
    def process_prediction_results(texts: List[str], topics: List[str], metadata: Dict = None) -> Dict:
        """Process prediction results for display"""
        if metadata is None:
            metadata = {}
        
        results_df = pd.DataFrame({
            "Text": texts,
            "Predicted Topic": topics,
            "Text Length": [len(text) for text in texts]
        })
        
        # Topic distribution
        topic_counts = pd.Series(topics).value_counts()
        
        return {
            "dataframe": results_df,
            "topic_distribution": topic_counts.to_dict(),
            "summary": {
                "total_texts": len(texts),
                "unique_topics": len(topic_counts),
                "avg_text_length": results_df["Text Length"].mean(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **metadata
            }
        }
    
    @staticmethod
    def process_scraped_data(data: List[Dict]) -> Dict:
        """Process scraped data for display"""
        if not data:
            return {"dataframe": pd.DataFrame(), "summary": {}}
        
        df = pd.DataFrame(data)
        
        summary = {
            "total_records": len(df),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        # Add year statistics if available
        if 'year' in df.columns:
            summary["year_range"] = {
                "min": df['year'].min(),
                "max": df['year'].max(),
                "distribution": df['year'].value_counts().to_dict()
            }
        
        # Add text statistics if available
        text_columns = [col for col in df.columns if col in ['title', 'abstract', 'text', 'content']]
        if text_columns:
            text_lengths = []
            for col in text_columns:
                if col in df.columns:
                    lengths = df[col].astype(str).str.len()
                    text_lengths.extend(lengths.tolist())
            
            if text_lengths:
                summary["text_stats"] = {
                    "avg_length": sum(text_lengths) / len(text_lengths),
                    "min_length": min(text_lengths),
                    "max_length": max(text_lengths),
                    "total_chars": sum(text_lengths)
                }
        
        return {"dataframe": df, "summary": summary}

def display_status_message(message: str, status_type: str = "info"):
    """Display a status message with appropriate styling"""
    css_class = {
        "success": "status-success",
        "error": "status-error",
        "warning": "status-warning",
        "info": "status-info"
    }.get(status_type, "status-info")
    
    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)

def format_timestamp(timestamp: str = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

def validate_file_upload(uploaded_file, allowed_types: List[str] = None) -> Tuple[bool, str, Any]:
    """Validate uploaded file and return processed data"""
    if allowed_types is None:
        allowed_types = ['csv', 'json', 'txt']
    
    if uploaded_file is None:
        return False, "No file uploaded", None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_types:
        return False, f"Unsupported file type. Allowed types: {', '.join(allowed_types)}", None
    
    try:
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
            if 'text' in df.columns:
                return True, "CSV file loaded successfully", df['text'].dropna().tolist()
            else:
                return False, "CSV file must have a 'text' column", None
        
        elif file_extension == 'json':
            data = json.load(uploaded_file)
            if isinstance(data, list):
                return True, "JSON file loaded successfully", [str(item) for item in data if item]
            else:
                return False, "JSON file must contain an array of texts", None
        
        elif file_extension == 'txt':
            content = uploaded_file.read().decode('utf-8')
            texts = [line.strip() for line in content.split('\n') if line.strip()]
            return True, "Text file loaded successfully", texts
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None
    
    return False, "Unknown error processing file", None

# Initialize global instances
api_client = APIClient()
service_monitor = ServiceMonitor()
file_manager = FileManager()
data_processor = DataProcessor()
