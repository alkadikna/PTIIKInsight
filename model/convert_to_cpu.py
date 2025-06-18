import joblib
import torch
import os
import logging
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_model_to_cpu():
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CUDA_MODEL_PATH = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20.pkl")
    CPU_MODEL_PATH = os.path.join(BASE_DIR, "bertopic_model_all-MiniLM-min20_cpu.pkl")
    
    if not os.path.exists(CUDA_MODEL_PATH):
        logger.error(f"Model file not found: {CUDA_MODEL_PATH}")
        return False
    
    try:
        logger.info("Loading CUDA model with CPU mapping...")
        
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        
        # Method 1: Try with custom pickle loader that maps tensors to CPU
        try:
            import pickle
            
            class CPUUnpickler(pickle.Unpickler):
                def persistent_load(self, pid):
                    if pid[0] == 'storage':
                        # Map storage to CPU
                        storage = torch.UntypedStorage.from_file(pid[1], False, pid[2])
                        typed_storage = torch.storage.TypedStorage(
                            wrap_storage=storage,
                            dtype=pid[3]
                        )
                        return typed_storage.cpu()
                    else:
                        return super().persistent_load(pid)
            
            # Load with CPU mapping
            with open(CUDA_MODEL_PATH, 'rb') as f:
                unpickler = CPUUnpickler(f)
                model = unpickler.load()
            
            logger.info("✓ Model loaded with CPU mapping")
            
        except Exception as e:
            logger.warning(f"Custom unpickler failed: {e}")
            
            # Method 2: Try patching torch.load to use CPU
            original_load = torch.load
            
            def cpu_load(f, map_location=None, **kwargs):
                return original_load(f, map_location='cpu', **kwargs)
            
            torch.load = cpu_load
            
            try:
                model = joblib.load(CUDA_MODEL_PATH)
                logger.info("✓ Model loaded with patched torch.load")
            finally:
                torch.load = original_load
        
        logger.info("Converting model components to CPU...")
        
        # Convert embedding model to CPU
        if hasattr(model, 'embedding_model'):
            embedding_model = model.embedding_model
            
            # Move to CPU if it's a PyTorch model
            if hasattr(embedding_model, 'to'):
                embedding_model.to('cpu')
                logger.info("✓ Moved embedding model to CPU")
            
            # Update device attributes
            if hasattr(embedding_model, 'device'):
                embedding_model.device = torch.device('cpu')
            if hasattr(embedding_model, '_target_device'):
                embedding_model._target_device = torch.device('cpu')
            
            # Handle model modules
            if hasattr(embedding_model, '_modules'):
                for name, module in embedding_model._modules.items():
                    if hasattr(module, 'to'):
                        module.to('cpu')
                        logger.info(f"✓ Moved {name} to CPU")
        
        # Save CPU-compatible model
        logger.info(f"Saving CPU-compatible model to {CPU_MODEL_PATH}")
        joblib.dump(model, CPU_MODEL_PATH)
        
        # Test the converted model
        logger.info("Testing converted model...")
        test_texts = ["test machine learning", "artificial intelligence"]
        topics, probs = model.transform(test_texts)
        logger.info(f"✓ Model test successful: {len(topics)} predictions made")
        
        # Replace original model with CPU version
        logger.info("Replacing original model with CPU version...")
        os.rename(CUDA_MODEL_PATH, f"{CUDA_MODEL_PATH}.cuda_backup")
        os.rename(CPU_MODEL_PATH, CUDA_MODEL_PATH)
        
        logger.info("✅ Model conversion completed successfully!")
        logger.info(f"Original CUDA model backed up as: {CUDA_MODEL_PATH}.cuda_backup")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model conversion failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== BERTopic Model CPU Conversion ===")
    success = convert_model_to_cpu()
    
    if success:
        logger.info("Model is now CPU-compatible!")
    else:
        logger.error("Conversion failed. Please check the logs above.")
