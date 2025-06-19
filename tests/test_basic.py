import pytest
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_project_structure():
    """Test that essential project files exist"""
    essential_files = [
        'docker-compose.yml',
        'requirements.txt',
        'api/main.py',
        'model/predict.py',
        'mlflow/drift_monitor.py',
        'mlflow/combined_service.py',
        'Dockerfile',
        'mlflow/Dockerfile'
    ]
    
    for file_path in essential_files:
        assert os.path.exists(file_path), f"Essential file missing: {file_path}"

def test_docker_compose_syntax():
    """Test docker-compose.yml syntax and structure"""
    import yaml
    
    with open('docker-compose.yml', 'r') as f:
        compose_config = yaml.safe_load(f)
        
    # Check basic structure
    assert 'services' in compose_config
    assert 'volumes' in compose_config
    
    # Check required services
    required_services = ['fastapi-app', 'prometheus', 'grafana', 'mlflow-drift-monitor']
    for service in required_services:
        assert service in compose_config['services'], f"Service missing: {service}"
        
    # Check FastAPI service
    fastapi_service = compose_config['services']['fastapi-app']
    assert 'ports' in fastapi_service
    assert 'volumes' in fastapi_service
    assert 'restart' in fastapi_service
    
    # Check MLflow service
    mlflow_service = compose_config['services']['mlflow-drift-monitor']
    assert 'ports' in mlflow_service
    assert 'volumes' in mlflow_service
    assert 'environment' in mlflow_service

def test_requirements_files():
    """Test that all requirements files are valid"""
    req_files = [
        'requirements.txt',
        'api/requirements.txt', 
        'dashboard/requirements.txt',
        'mlflow/requirements.txt'
    ]
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                lines = f.readlines()
                
            # Check that requirements are not empty
            valid_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            assert len(valid_lines) > 0, f"Requirements file is empty: {req_file}"
            
            # Check format of each requirement
            for line in valid_lines:
                assert '==' in line or '>=' in line, f"Invalid requirement format in {req_file}: {line}"

def test_dockerfile_syntax():
    """Test Dockerfile syntax"""
    dockerfiles = ['Dockerfile', 'mlflow/Dockerfile']
    
    for dockerfile in dockerfiles:
        if os.path.exists(dockerfile):
            with open(dockerfile, 'r') as f:
                content = f.read()
                
            # Check basic Dockerfile commands
            assert 'FROM' in content, f"Missing FROM instruction in {dockerfile}"
            assert 'WORKDIR' in content, f"Missing WORKDIR instruction in {dockerfile}"
            
def test_json_files_validity():
    """Test that JSON files are valid"""
    json_files = []
    
    # Find all JSON files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.json') and not file.startswith('.'):
                json_files.append(os.path.join(root, file))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

def test_python_files_syntax():
    """Test that Python files have valid syntax"""
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {py_file}: {e}")
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(py_file, 'r', encoding='latin-1') as f:
                    compile(f.read(), py_file, 'exec')
            except Exception as e:
                pytest.fail(f"Could not parse {py_file}: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
