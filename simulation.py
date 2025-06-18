import requests
import time
import random
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_endpoints(base_url="http://localhost:8000"):
    sample_texts = [
        "machine learning algorithms for data analysis",
        "deep neural networks and artificial intelligence",
        "web development using modern frameworks",
        "database optimization and performance tuning",
        "cybersecurity threats and protection methods",
        "cloud computing infrastructure and services",
        "mobile application development best practices",
        "data mining and knowledge discovery techniques",
        "computer vision and image processing",
        "natural language processing applications"
    ]
    
    logger.info("Starting API testing simulation...")
    
    for i in range(20):
        try:
            logger.info(f"Request batch {i+1}/20")
            
            # 1. Health check
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Health check successful")
            else:
                logger.warning(f"✗ Health check failed: {response.status_code}")
            
            # 2. Get data endpoint
            response = requests.get(f"{base_url}/data", timeout=10)
            if response.status_code == 200:
                logger.info("✓ Data endpoint successful")
            else:
                logger.info(f"ℹ Data endpoint returned: {response.status_code}")
            
            # 3. Prediction endpoint with random texts
            texts = random.sample(sample_texts, random.randint(1, 3))
            prediction_data = {"texts": texts}
            
            response = requests.post(
                f"{base_url}/predict",
                json=prediction_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Prediction successful for {len(texts)} texts")
                logger.info(f"  Topics: {result.get('topics', [])[:2]}...")  # Show first 2 topics
            else:
                logger.warning(f"✗ Prediction failed: {response.status_code}")
            
            # 4. Occasionally trigger scraping (every 5th request)
            if i % 5 == 0:
                response = requests.post(f"{base_url}/scrape", timeout=5)
                if response.status_code == 200:
                    logger.info("✓ Scraping request sent")
                else:
                    logger.warning(f"✗ Scraping request failed: {response.status_code}")
            
            # 5. Update model accuracy (simulate)
            if i % 3 == 0:
                accuracy = random.uniform(0.75, 0.95)
                response = requests.post(f"{base_url}/update-accuracy", params={"accuracy": accuracy}, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✓ Model accuracy updated to {accuracy:.3f}")
                else:
                    logger.warning(f"✗ Accuracy update failed: {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            logger.error("✗ Cannot connect to API. Make sure it's running at http://localhost:8000")
        except requests.exceptions.Timeout:
            logger.warning("⚠ Request timed out")
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
        
        # Random delay between requests
        delay = random.uniform(2, 5)
        logger.info(f"Waiting {delay:.1f} seconds before next batch...")
        time.sleep(delay)
    
    logger.info("API testing simulation completed!")

def check_grafana_metrics(grafana_url="http://localhost:3000"):
    try:
        # Check Grafana health
        response = requests.get(f"{grafana_url}/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✓ Grafana is accessible")
            logger.info(f"  Dashboard: {grafana_url}/d/ptiik-insight-dashboard")
            logger.info("  Login: admin/admin")
            return True
        else:
            logger.error(f"✗ Grafana health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Cannot connect to Grafana: {e}")
        return False

def check_prometheus_metrics(prometheus_url="http://localhost:9090"):
    try:
        # Get available metrics
        response = requests.get(f"{prometheus_url}/api/v1/label/__name__/values", timeout=5)
        if response.status_code == 200:
            metrics = response.json().get("data", [])
            custom_metrics = [m for m in metrics if m.startswith(("model_", "http_", "scraping_"))]
            logger.info(f"✓ Prometheus collecting {len(custom_metrics)} custom metrics")
            
            # Show some example metrics
            for metric in custom_metrics[:5]:
                logger.info(f"  - {metric}")
            
            return True
        else:
            logger.error(f"✗ Prometheus metrics check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Cannot connect to Prometheus: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== PTIIK Insight Grafana Testing ===")
    
    logger.info("\n1. Checking services...")
    grafana_ok = check_grafana_metrics()
    prometheus_ok = check_prometheus_metrics()
    
    if not grafana_ok:
        logger.error("Grafana is not accessible. Make sure it's running:")
        logger.error("  docker-compose up -d grafana")
        
    if not prometheus_ok:
        logger.error("Prometheus is not accessible. Make sure it's running:")
        logger.error("  docker-compose up -d prometheus")
    
    logger.info("\n2. Generating API traffic...")
    test_api_endpoints()
    
    logger.info("\n=== Testing Complete ===")
    logger.info("Check your dashboards:")
    logger.info("- Grafana: http://localhost:3000 (admin/admin)")
    logger.info("- Prometheus: http://localhost:9090")
    logger.info("- API Metrics: http://localhost:8000/metrics")
