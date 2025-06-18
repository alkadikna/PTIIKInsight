import pandas as pd
import os
import logging
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_model():
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "../data/cleaned_data.csv")
    MODEL_PATH = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20_retrained.pkl")
    
    try:
        logger.info("Loading training data...")
        if not os.path.exists(DATA_PATH):
            logger.error(f"Training data not found: {DATA_PATH}")
            return False
        
        df = pd.read_csv(DATA_PATH)
        logger.info(f"Loaded {len(df)} documents for training")
        if 'title' in df.columns:
            texts = df['title'].fillna('').astype(str).tolist()
        elif 'Judul' in df.columns:
            texts = df['Judul'].fillna('').astype(str).tolist()
        else:
            logger.error(f"No title column found. Available columns: {df.columns.tolist()}")
            return False
            
        texts = [text for text in texts if text.strip()]  # Remove empty texts
        
        logger.info(f"Training on {len(texts)} valid texts")
        
        # Create embedding model (CPU compatible)
        logger.info("Creating embedding model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Force to CPU
        embedding_model.to('cpu')
        
        # Create BERTopic model
        logger.info("Creating BERTopic model...")
        topic_model = BERTopic(
            embedding_model=embedding_model,
            min_topic_size=20,
            verbose=True
        )
        
        # Train the model
        logger.info("Training BERTopic model...")
        topics, probabilities = topic_model.fit_transform(texts)
        
        logger.info(f"Training completed. Found {len(set(topics))} topics")
        
        # Save the model
        logger.info(f"Saving model to {MODEL_PATH}")
        joblib.dump(topic_model, MODEL_PATH)
        
        # Test the saved model
        logger.info("Testing saved model...")
        loaded_model = joblib.load(MODEL_PATH)
        test_topics, _ = loaded_model.transform(["machine learning algorithms"])
        logger.info(f"Test successful. Test topic: {test_topics}")
        
        # Replace the original model
        original_model_path = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20.pkl")
        backup_path = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20_backup.pkl")
        
        # Backup original
        if os.path.exists(original_model_path):
            os.rename(original_model_path, backup_path)
            logger.info(f"Original model backed up to {backup_path}")
        
        # Replace with retrained model
        os.rename(MODEL_PATH, original_model_path)
        logger.info(f"Retrained model installed as {original_model_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        return False

if __name__ == "__main__":
    if retrain_model():
        print("✅ Model retrained successfully!")
    else:
        print("❌ Model retraining failed!")
