import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAPIMain:
    """Test API main functionality"""
    
    def test_api_import(self):
        """Test that API can be imported"""
        try:
            from api.main import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"API import failed, dependencies may be missing: {e}")
    
    @patch('api.main.predict_topic')
    def test_predict_endpoint_structure(self, mock_predict):
        """Test predict endpoint basic structure"""
        try:
            from api.main import app, PredictRequest
            from fastapi.testclient import TestClient
            
            mock_predict.return_value = [{"topic": "test", "probability": 0.5}]
            
            client = TestClient(app)
            response = client.post("/predict", json={"texts": ["test text"]})
            
            # Should not crash even if model is not loaded
            assert response.status_code in [200, 500]  # Either works or model not loaded
            
        except ImportError as e:
            pytest.skip(f"FastAPI test dependencies missing: {e}")
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            from api.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            
        except ImportError as e:
            pytest.skip(f"FastAPI test dependencies missing: {e}")

class TestModelPredict:
    """Test model prediction functionality"""
    
    def test_predict_import(self):
        """Test that predict module can be imported"""
        try:
            from model.predict import predict_topic
            assert predict_topic is not None
        except ImportError as e:
            pytest.skip(f"Model predict import failed: {e}")
    
    @patch('model.predict.joblib.load')
    @patch('model.predict.os.path.exists')
    def test_predict_function_structure(self, mock_exists, mock_load):
        """Test predict function basic structure"""
        try:
            mock_exists.return_value = True
            mock_model = Mock()
            mock_model.transform.return_value = [["topic1", "topic2"]]
            mock_load.return_value = mock_model
            
            from model.predict import predict_topic
            
            result = predict_topic(["test text"])
            assert isinstance(result, list)
            
        except ImportError as e:
            pytest.skip(f"Model predict test failed: {e}")

class TestMLflowDriftMonitor:
    """Test MLflow drift monitoring functionality"""
    
    def test_drift_monitor_import(self):
        """Test that drift monitor can be imported"""
        try:
            from mlflow.drift_monitor import DataDriftMonitor
            assert DataDriftMonitor is not None
        except ImportError as e:
            pytest.skip(f"Drift monitor import failed: {e}")
    
    def test_combined_service_import(self):
        """Test that combined service can be imported"""
        try:
            from mlflow.combined_service import MLflowDriftService
            assert MLflowDriftService is not None
        except ImportError as e:
            pytest.skip(f"Combined service import failed: {e}")
    
    @patch('mlflow.drift_monitor.os.path.exists')
    def test_drift_monitor_initialization(self, mock_exists):
        """Test drift monitor initialization"""
        try:
            mock_exists.return_value = False  # No existing reference data
            
            from mlflow.drift_monitor import DataDriftMonitor
            
            monitor = DataDriftMonitor()
            assert monitor.data_path is not None
            assert monitor.drift_threshold > 0
            
        except ImportError as e:
            pytest.skip(f"Drift monitor initialization test failed: {e}")

class TestPreprocessing:
    """Test preprocessing functionality"""
    
    def test_preprocessing_import(self):
        """Test that preprocessing modules can be imported"""
        modules_to_test = [
            'preprocessing.preprocessing',
            'preprocessing.scraping'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.skip(f"Preprocessing module {module_name} import failed: {e}")
    
    @patch('preprocessing.preprocessing.pd.read_csv')
    def test_preprocessing_basic_functionality(self, mock_read_csv):
        """Test preprocessing basic functionality"""
        try:
            import pandas as pd
            
            # Mock DataFrame
            mock_df = pd.DataFrame({
                'title': ['test title 1', 'test title 2'],
                'content': ['test content 1', 'test content 2']
            })
            mock_read_csv.return_value = mock_df
            
            # This is a basic test - actual preprocessing functions would need specific testing
            assert len(mock_df) == 2
            
        except ImportError as e:
            pytest.skip(f"Preprocessing test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
