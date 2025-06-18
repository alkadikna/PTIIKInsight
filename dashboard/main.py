import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import subprocess
import sys
import os
import threading

# Import dashboard utilities
try:
    from dashboard.utils import (
        api_client, service_monitor, file_manager, data_processor,
        display_status_message, format_timestamp, validate_file_upload
    )
    from dashboard.config import *
except ImportError:
    # Fallback - create simple versions
    class SimpleAPIClient:
        def check_health(self):
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=5)
                return response.status_code == 200, response.json() if response.status_code == 200 else None
            except:
                return False, None
        
        def predict_topics(self, texts):
            try:
                import requests
                response = requests.post(
                    "http://localhost:8000/predict",
                    json={"texts": texts},
                    timeout=30
                )
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, f"API Error: {response.status_code}"
            except Exception as e:
                return False, str(e)
        
        def start_scraping(self):
            try:
                import requests
                response = requests.post("http://localhost:8000/scrape", timeout=10)
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, f"API Error: {response.status_code}"
            except Exception as e:
                return False, str(e)
        
        def get_data(self):
            try:
                import requests
                response = requests.get("http://localhost:8000/data", timeout=10)
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, f"API Error: {response.status_code}"
            except Exception as e:
                return False, str(e)
    
    class SimpleServiceMonitor:
        def check_all_services(self):
            import requests
            services = {
                "API": {"url": "http://localhost:8000/health", "status": False},
                "Grafana": {"url": "http://localhost:3000/api/health", "status": False},
                "Prometheus": {"url": "http://localhost:9090/api/v1/query?query=up", "status": False}
            }
            
            for service, config in services.items():
                try:
                    response = requests.get(config["url"], timeout=3)
                    config["status"] = response.status_code == 200
                except:
                    config["status"] = False
            
            return services
        
        def get_health_percentage(self):
            services = self.check_all_services()
            total_services = len(services)
            online_services = sum(1 for s in services.values() if s["status"])
            return (online_services / total_services) * 100 if total_services > 0 else 0    
    api_client = SimpleAPIClient()
    service_monitor = SimpleServiceMonitor()
    
    class SimpleDataProcessor:
        def process_scraped_data(self, data):
            if not data:
                return {"dataframe": pd.DataFrame(), "summary": {}}
            
            df = pd.DataFrame(data)
            
            summary = {
                "total_records": len(df),
                "memory_usage_mb": 0.1  # placeholder
            }
            
            # Add year statistics if available
            if 'year' in df.columns:
                summary["year_range"] = {
                    "min": df['year'].min(),
                    "max": df['year'].max(),
                    "distribution": df['year'].value_counts().to_dict()
                }
            
            return {"dataframe": df, "summary": summary}
    
    data_processor = SimpleDataProcessor()
    
    class SimpleFileManager:
        def get_project_root(self):
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        def get_model_info(self):
            project_root = self.get_project_root()
            model_path = os.path.join(project_root, "model", "bertopic_model_all-MiniLM-min20.pkl")
            
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
    
    file_manager = SimpleFileManager()
    
    # Simple fallback functions
    def validate_file_upload(uploaded_file, allowed_types):
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
            
        except Exception as e:
            return False, f"Error reading file: {str(e)}", None
        
        return False, "Unknown error processing file", None

# Configuration constants
DASHBOARD_TITLE = "PTIIK Insight Dashboard"
DASHBOARD_ICON = "🔬"
DASHBOARD_LAYOUT = "wide"
TRAINING_TIMEOUT = 1800

# Page config
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=DASHBOARD_ICON,
    layout=DASHBOARD_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
if 'prediction_results' not in st.session_state:
    st.session_state.prediction_results = []
if 'scraping_status' not in st.session_state:
    st.session_state.scraping_status = None
if 'training_status' not in st.session_state:
    st.session_state.training_status = None

def run_training_background():
    """Run model training in background"""
    try:
        # Change to model directory and run training
        project_root = file_manager.get_project_root()
        model_dir = os.path.join(project_root, "model")
        result = subprocess.run(
            [sys.executable, "train.py"], 
            cwd=model_dir,
            capture_output=True,
            text=True,
            timeout=TRAINING_TIMEOUT
        )
        
        if result.returncode == 0:
            st.session_state.training_status = {"success": True, "message": "Training completed successfully"}
        else:
            st.session_state.training_status = {"success": False, "message": f"Training failed: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        st.session_state.training_status = {"success": False, "message": "Training timed out"}
    except Exception as e:
        st.session_state.training_status = {"success": False, "message": f"Training error: {str(e)}"}

def main():
    # Header
    st.markdown(f'<h1 class="main-header">{DASHBOARD_ICON} {DASHBOARD_TITLE}</h1>', unsafe_allow_html=True)    # Sidebar navigation
    with st.sidebar:
        st.image("https://j-ptiik.ub.ac.id/public/journals/1/pageHeaderLogoImage_id_ID.png", width=200)
        st.markdown("---")
        
        # Navigation buttons
        if st.button("📊 Overview", use_container_width=True):
            st.session_state.page = "Overview"
        if st.button("🤖 Prediction", use_container_width=True):
            st.session_state.page = "Prediction"
        if st.button("🕷️ Crawling", use_container_width=True):
            st.session_state.page = "Crawling"
        if st.button("🎯 Training", use_container_width=True):
            st.session_state.page = "Training"
        
        # Initialize page if not set
        if 'page' not in st.session_state:
            st.session_state.page = "Overview"
        
        selected = st.session_state.page
      # Main content based on selection
    if selected == "Overview":
        show_overview()
    elif selected == "Prediction":
        show_prediction()
    elif selected == "Crawling":
        show_crawling()
    elif selected == "Training":
        show_training()

def show_overview():
    """Show system overview"""
    st.header("📊 System Overview")
    
    # Check services status
    services = service_monitor.check_all_services()
    
    # Service status cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_status = services["API"]["status"]
        st.metric(
            label="🚀 API Service",
            value="Online" if api_status else "Offline",
            delta="Healthy" if api_status else "Check Connection"
        )
        
    with col2:
        grafana_status = services["Grafana"]["status"]
        st.metric(
            label="📈 Grafana",
            value="Online" if grafana_status else "Offline",
            delta="Ready" if grafana_status else "Not Available"        )
        
    with col3:
        prometheus_status = services["Prometheus"]["status"]
        st.metric(
            label="📊 Prometheus",
            value="Online" if prometheus_status else "Offline",
            delta="Collecting" if prometheus_status else "Not Available"
        )

def show_prediction():
    """Show prediction interface"""
    st.header("🤖 Topic Prediction")
    
    # Check API status
    api_healthy, health_data = api_client.check_health()
    
    if not api_healthy:
        st.error("❌ API is not available. Please start the API service first.")
        st.code("uvicorn api.main:app --reload", language="bash")
        return
    
    st.success("✅ API is running and ready for predictions")
    
    # Prediction methods
    prediction_method = st.radio(
        "Choose prediction method:",
        ["Single Text", "Multiple Texts", "Upload File"],
        horizontal=True
    )
    
    texts_to_predict = []
    
    if prediction_method == "Single Text":
        text_input = st.text_area(
            "Enter text for topic prediction:",
            placeholder="Enter research paper title or abstract here...",
            height=150
        )
        if text_input.strip():
            texts_to_predict = [text_input.strip()]
            
    elif prediction_method == "Multiple Texts":
        st.info("Enter each text on a new line")
        multi_text = st.text_area(
            "Enter multiple texts (one per line):",
            placeholder="Text 1\nText 2\nText 3...",
            height=200        )
        if multi_text.strip():
            texts_to_predict = [line.strip() for line in multi_text.split('\n') if line.strip()]
            
    elif prediction_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload CSV or JSON file",
            type=['csv', 'json'],
            help="CSV should have a 'text' column, JSON should be an array of texts"
        )
        
        if uploaded_file:
            success, message, texts = validate_file_upload(uploaded_file, ['csv', 'json'])
            if success:
                texts_to_predict = texts
                st.success(message)
            else:
                st.error(message)
    
    # Show preview of texts
    if texts_to_predict:
        st.subheader(f"📝 Preview ({len(texts_to_predict)} texts)")
        preview_df = pd.DataFrame({
            "Index": range(1, len(texts_to_predict) + 1),
            "Text Preview": [text[:100] + "..." if len(text) > 100 else text for text in texts_to_predict]
        })
        st.dataframe(preview_df, use_container_width=True)
        
        # Prediction button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Run Prediction", type="primary"):
                with st.spinner("Making predictions..."):
                    success, result = api_client.predict_topics(texts_to_predict)
                    
                    if success:
                        st.success("✅ Prediction completed successfully!")
                        
                        # Store results in session state
                        st.session_state.prediction_results = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "input_count": len(texts_to_predict),
                            "texts": texts_to_predict,
                            "topics": result["topics"],
                            "prediction_time": result.get("prediction_time", 0)
                        }
                    else:
                        st.error(f"❌ Prediction failed: {result}")
        
        with col2:
            st.info(f"⚡ Ready to predict {len(texts_to_predict)} texts")
    
    # Show results if available
    if st.session_state.prediction_results:
        st.subheader("📊 Prediction Results")
        
        results = st.session_state.prediction_results
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Texts Processed", results["input_count"])
        with col2:
            st.metric("⏱️ Processing Time", f"{results['prediction_time']:.2f}s")
        with col3:
            st.metric("📅 Last Prediction", results["timestamp"])
        
        # Results table
        results_df = pd.DataFrame({
            "Text": results["texts"],
            "Predicted Topic": results["topics"]
        })
        
        st.dataframe(results_df, use_container_width=True)
        
        # Topic distribution chart
        topic_counts = pd.Series(results["topics"]).value_counts()
        
        fig = px.bar(
            x=topic_counts.index,
            y=topic_counts.values,
            title="Topic Distribution",
            labels={"x": "Topics", "y": "Count"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Download results
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv_data,
            file_name=f"prediction_results_{results['timestamp'].replace(':', '-')}.csv",
            mime="text/csv"
        )

def show_crawling():
    """Show data crawling interface"""
    st.header("🕷️ Data Crawling")
    
    # Check API status
    api_healthy, health_data = api_client.check_health()
    
    if not api_healthy:
        st.error("❌ API is not available. Please start the API service first.")
        return
    
    # Crawling controls
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎛️ Controls")
        
        if st.button("🚀 Start Crawling", type="primary"):
            with st.spinner("Starting crawling process..."):
                success, result = api_client.start_scraping()
                
                if success:
                    st.success("✅ Crawling started successfully!")
                    st.session_state.scraping_status = {
                        "status": "running",
                        "message": result.get("message", "Crawling in progress"),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                else:
                    st.error(f"❌ Failed to start crawling: {result}")
                    st.session_state.scraping_status = {
                        "status": "error",
                        "message": result,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    with col2:
        st.subheader("📊 Status")
        
        if st.session_state.scraping_status:
            status = st.session_state.scraping_status
            
            if status["status"] == "running":
                st.info(f"🔄 {status['message']}")
            elif status["status"] == "error":
                st.error(f"❌ {status['message']}")
            else:
                st.success(f"✅ {status['message']}")
                
            st.text(f"Last update: {status['timestamp']}")
      # Current data overview
    st.subheader("📋 Current Data")
    
    with st.spinner("Loading current data..."):
        success, data_result = api_client.get_data()
        
        if success and data_result.get("data"):
            # Process data using utility
            processed_data = data_processor.process_scraped_data(data_result["data"])
            df = processed_data["dataframe"]
            summary = processed_data["summary"]
              # Data summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Total Records", summary.get("total_records", 0))
            with col2:
                if summary.get("year_range"):
                    st.metric("📅 Latest Year", summary["year_range"]["max"])
                else:
                    st.metric("📅 Data Status", "Available")
            with col3:
                st.metric("💾 Data Size", f"{summary.get('memory_usage_mb', 0):.1f} MB")
            
            # Data preview
            st.subheader("👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
              # Data statistics
            if len(df) > 0:
                st.subheader("📈 Data Statistics")
                
                # Year distribution if available
                if summary.get("year_range"):
                    year_dist = summary["year_range"]["distribution"]
                    fig = px.bar(
                        x=list(year_dist.keys()),
                        y=list(year_dist.values()),
                        title="Papers by Year",
                        labels={"x": "Year", "y": "Number of Papers"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Text length distribution if available
                if summary.get("text_stats"):
                    text_stats = summary["text_stats"]
                    st.metric("📝 Average Text Length", f"{text_stats['avg_length']:.0f} chars")
            
            # Download option
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Current Data",
                data=csv_data,
                file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
        else:
            if success:
                st.info("📭 No data available yet. Start crawling to collect data.")
            else:
                st.error(f"❌ Failed to load data: {data_result}")

def show_training():
    """Show model training interface"""
    st.header("🎯 Model Training")
    
    st.info("🚧 Model training is a resource-intensive process that may take 15-30 minutes.")
    
    # Training controls
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎛️ Training Controls")
        
        # Training configuration (simplified)
        st.selectbox(
            "Embedding Model",
            ["sentence-transformers/all-MiniLM-L6-v2", "multilingual-e5-large"],
            help="Pre-trained embedding model to use"
        )
        
        min_topic_size = st.slider(
            "Minimum Topic Size",
            min_value=5,
            max_value=50,
            value=20,
            help="Minimum number of documents per topic"
        )
        
        if st.button("🚀 Start Training", type="primary"):
            if st.session_state.training_status and st.session_state.training_status.get("status") == "running":
                st.warning("⚠️ Training is already in progress!")
            else:
                st.session_state.training_status = {
                    "status": "running",
                    "message": "Training started...",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Start training in background thread
                training_thread = threading.Thread(target=run_training_background)
                training_thread.daemon = True
                training_thread.start()
                
                st.success("✅ Training started! Check status below for updates.")
                st.rerun()
        
        if st.button("🔄 Check Status"):
            st.rerun()
    
    with col2:
        st.subheader("📊 Training Status")
        
        if st.session_state.training_status:
            status = st.session_state.training_status
            
            if status.get("status") == "running":
                st.info("🔄 Training in progress... This may take a while.")
                st.progress(0.5)  # Indeterminate progress
            elif status.get("success"):
                st.success("✅ Training completed successfully!")
            else:
                st.error(f"❌ Training failed: {status.get('message', 'Unknown error')}")
                
            st.text(f"Last update: {status.get('timestamp', 'Unknown')}")
        else:
            st.info("📭 No training sessions yet.")
      # Model information
    st.subheader("🧠 Current Model Info")
    
    # Check if model file exists
    model_info = file_manager.get_model_info()
    
    if model_info["exists"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Model Size", f"{model_info['size_mb']:.1f} MB")
        with col2:
            st.metric("📅 Last Modified", model_info['modified'].strftime("%Y-%m-%d"))
        with col3:
            st.metric("✅ Status", "Available")
    else:
        st.warning("⚠️ No trained model found. Please train a model first.")

if __name__ == "__main__":
    main()
