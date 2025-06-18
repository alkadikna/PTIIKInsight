import joblib
import pandas as pd
import os
import logging
import torch
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20.pkl")

# Global model variable
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model file not found at {MODEL_PATH}")
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        
        logger.info(f"Loading BERTopic model from {MODEL_PATH}")
        
        # Check if CUDA is available
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            logger.info("Loading model with CUDA support")
            _model = joblib.load(MODEL_PATH)
        else:
            logger.info("Loading model for CPU-only environment")
            # Try loading with CPU mapping - simplified approach
            try:
                # Set environment to force CPU usage
                os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
                
                # Method 1: Patch torch.load to force CPU mapping
                original_load = torch.load
                
                def cpu_load(f, map_location=None, **kwargs):
                    return original_load(f, map_location='cpu', **kwargs)
                
                torch.load = cpu_load
                
                try:
                    # Also patch sklearn imports for compatibility
                    import sklearn.metrics._dist_metrics
                    
                    # Try to add missing attributes for compatibility
                    if not hasattr(sklearn.metrics._dist_metrics, 'EuclideanDistance'):
                        from sklearn.metrics import DistanceMetric
                        sklearn.metrics._dist_metrics.EuclideanDistance = DistanceMetric.get_metric('euclidean')
                    
                    _model = joblib.load(MODEL_PATH)
                    logger.info("Model loaded successfully with CPU mapping")
                finally:
                    # Restore original torch.load
                    torch.load = original_load
                    
            except Exception as cpu_error:
                logger.warning(f"CPU loading failed: {cpu_error}")
                
                # Method 2: Try loading the CPU-converted version if it exists
                cpu_model_path = MODEL_PATH.replace('.pkl', '_cpu.pkl')
                if os.path.exists(cpu_model_path):
                    logger.info(f"Trying CPU-converted model: {cpu_model_path}")
                    _model = joblib.load(cpu_model_path)
                    logger.info("CPU-converted model loaded successfully")
                else:
                    logger.error("No CPU-compatible model available")
                    raise cpu_error
        
        logger.info("BERTopic model loaded successfully")
        
        # Verify model is working
        try:
            # Test with a simple prediction
            test_text = ["test text for model verification"]
            if hasattr(_model, 'transform'):
                _ = _model.transform(test_text)
                logger.info("Model verification successful")
            else:
                logger.error("Model loaded but transform method not available")
                raise AttributeError("Model does not have transform method")
        except Exception as verify_error:
            logger.error(f"Model verification failed: {verify_error}")
            raise verify_error
            
    return _model

def predict_topic(texts: List[str]) -> List[str]:
    try:
        if not texts:
            raise ValueError("Empty text list provided")
        
        # Load model if not already loaded
        model = load_model()
        
        # Create dataframe and apply basic preprocessing
        df = pd.DataFrame({'text': texts})
        
        # Basic text cleaning (same as preprocessing)
        df['text'] = df['text'].fillna('')
        df['text'] = df['text'].astype(str)
        
        # Make predictions
        logger.info(f"Making predictions for {len(texts)} texts using BERTopic model")
        
        topics, probabilities = model.transform(df['text'].tolist())
        
        # Convert topic numbers to topic labels/names
        topic_labels = []
        for topic in topics:
            if topic == -1:
                topic_labels.append("Outlier")
            else:
                # Get topic words for better representation
                try:
                    topic_words = model.get_topic(topic)
                    if topic_words:
                        # Create label from top 3 words
                        top_words = [word for word, _ in topic_words[:3]]
                        topic_labels.append(f"Topic_{topic}: {', '.join(top_words)}")
                    else:
                        topic_labels.append(f"Topic_{topic}")
                except Exception as topic_error:
                    logger.warning(f"Error getting topic words for topic {topic}: {topic_error}")
                    topic_labels.append(f"Topic_{topic}")
        
        logger.info(f"Predictions completed successfully for {len(texts)} texts")
        return topic_labels
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
