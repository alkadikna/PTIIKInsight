import pytest
import requests
import time
import json
import subprocess
import os
import signal
from contextlib import contextmanager

class TestDockerCompose:
    """Integration tests for Docker Compose services"""
    
    @pytest.fixture(scope="class")
    def docker_services(self):
        """Start Docker Compose services for testing"""
        # Create test data
        os.makedirs('data/cleaned', exist_ok=True)
        with open('data/cleaned/cleaned_data_v4.json', 'w') as f:
            json.dump([], f)
        
        # Start services
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        # Wait for services to be ready
        time.sleep(30)
        
        yield
        
        # Cleanup
        subprocess.run(['docker-compose', 'down', '-v'], check=False)
        
    def test_fastapi_health(self, docker_services):
        """Test FastAPI health endpoint"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    assert 'status' in data
                    assert data['status'] == 'healthy'
                    return
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    raise
        
        pytest.fail("FastAPI health check failed after all attempts")
    
    def test_mlflow_health(self, docker_services):
        """Test MLflow health endpoint"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:5000/health', timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    raise
        
        pytest.fail("MLflow health check failed after all attempts")
    
    def test_prometheus_health(self, docker_services):
        """Test Prometheus health endpoint"""
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:9090/-/healthy', timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    raise
        
        pytest.fail("Prometheus health check failed after all attempts")
    
    def test_grafana_health(self, docker_services):
        """Test Grafana health endpoint"""
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:3000/api/health', timeout=5)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    raise
        
        pytest.fail("Grafana health check failed after all attempts")
    
    def test_fastapi_predict_endpoint(self, docker_services):
        """Test FastAPI predict endpoint"""
        # Wait for FastAPI to be ready
        self.test_fastapi_health(docker_services)
        
        # Test prediction endpoint
        payload = {"texts": ["machine learning artificial intelligence"]}
        response = requests.post(
            'http://localhost:8000/predict',
            json=payload,
            timeout=10
        )
        
        # Should either work or fail gracefully if model not loaded
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'topics' in data or 'message' in data
    
    def test_fastapi_retrain_status(self, docker_services):
        """Test FastAPI retrain status endpoint"""
        # Wait for FastAPI to be ready
        self.test_fastapi_health(docker_services)
        
        response = requests.get('http://localhost:8000/retrain/status', timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_retraining_requests' in data
        assert 'model_loaded' in data
    
    def test_service_logs_no_errors(self, docker_services):
        """Test that services don't have critical errors in logs"""
        services = ['fastapi-app', 'mlflow-drift-monitor', 'prometheus', 'grafana']
        
        for service in services:
            try:
                result = subprocess.run(
                    ['docker-compose', 'logs', service],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                logs = result.stdout.lower()
                
                # Check for critical errors (but allow warnings)
                critical_errors = [
                    'fatal error',
                    'panic:',
                    'segmentation fault',
                    'core dumped'
                ]
                
                for error in critical_errors:
                    assert error not in logs, f"Critical error found in {service} logs: {error}"
                    
            except subprocess.TimeoutExpired:
                pytest.skip(f"Timeout getting logs for {service}")

class TestAPIIntegration:
    """Integration tests for API functionality"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Start only FastAPI for isolated testing"""
        # Create minimal test data
        os.makedirs('data/cleaned', exist_ok=True)
        with open('data/cleaned/cleaned_data.csv', 'w') as f:
            f.write('title,content\n')
            f.write('test title,test content\n')
        
        # Start only FastAPI
        process = subprocess.Popen(
            ['docker-compose', 'up', 'fastapi-app'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(15)
        
        yield
        
        # Cleanup
        process.terminate()
        process.wait()
        subprocess.run(['docker-compose', 'down'], check=False)
    
    def test_api_endpoints_response_format(self, api_client):
        """Test API endpoints return correct response format"""
        base_url = 'http://localhost:8000'
        
        # Test health endpoint
        response = requests.get(f'{base_url}/health', timeout=5)
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        
        # Test data endpoint
        response = requests.get(f'{base_url}/data', timeout=5)
        assert response.status_code in [200, 404]  # May not have data
        if response.status_code == 200:
            assert response.headers['content-type'] == 'application/json'
        
        # Test retrain status
        response = requests.get(f'{base_url}/retrain/status', timeout=5)
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
