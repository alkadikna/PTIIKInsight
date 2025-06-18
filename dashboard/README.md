# PTIIK Insight Dashboard

A comprehensive Streamlit web dashboard for the PTIIK Insight project that provides an intuitive interface for topic prediction, data crawling, model training, and system monitoring.

## Features

### 🏠 Overview
- System health monitoring
- Service status checks (API, Grafana, Prometheus)
- Quick action buttons
- Recent activity log

### 🤖 Topic Prediction
- Single text prediction
- Batch text prediction
- File upload support (CSV, JSON)
- Real-time results visualization
- Download prediction results

### 🕷️ Data Crawling
- Start/stop crawling processes
- Monitor crawling status
- View current data statistics
- Data visualization and analysis
- Download scraped data

### 🎯 Model Training
- Configure training parameters
- Background training process
- Training status monitoring
- Model information display

### 📊 System Monitoring
- Integration with Grafana dashboards
- Prometheus metrics visualization
- System resource monitoring
- Performance analytics

## Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- PTIIK Insight API running on localhost:8000

### Setup

1. Navigate to the project directory:
   ```bash
   cd PTIIKInsight
   ```

2. Install dashboard dependencies:
   ```bash
   pip install -r dashboard/requirements.txt
   ```

3. Or install manually:
   ```bash
   pip install streamlit streamlit-option-menu plotly pandas requests
   ```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r dashboard/requirements.txt
   ```

2. **Start the API service:**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start the dashboard:**
   ```bash
   cd dashboard
   streamlit run main.py --server.port 8501
   ```

4. **Access the dashboard:**
   - Open your browser and go to: http://localhost:8501
   - The dashboard will show the system status and available features

## Usage

### Method 1: Using the launcher scripts

**Windows Batch:**
```bash
start_dashboard.bat
```

**PowerShell:**
```powershell
.\start_dashboard.ps1
```

### Method 2: Manual startup

1. Navigate to the dashboard directory:
   ```bash
   cd dashboard
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run main.py --server.port 8501
   ```

3. Open your browser and go to: http://localhost:8501

## Configuration

The dashboard can be configured through `dashboard/config.py`:

- **API Settings**: Base URL, timeout settings
- **Monitoring URLs**: Grafana, Prometheus endpoints
- **UI Settings**: Layout, colors, chart sizes
- **File Paths**: Model, data, and script locations

## Dependencies

### Core Dependencies
- `streamlit`: Web application framework
- `streamlit-option-menu`: Navigation menu component
- `plotly`: Interactive data visualization
- `pandas`: Data manipulation and analysis
- `requests`: HTTP client for API communication

### Additional Dependencies
- `pillow`: Image processing
- `numpy`: Numerical computing
- `joblib`: Model serialization

## API Integration

The dashboard integrates with the PTIIK Insight API through the following endpoints:

- `GET /health`: Health check
- `POST /predict`: Topic prediction
- `POST /scrape`: Start crawling
- `GET /data`: Retrieve scraped data
- `POST /update-accuracy`: Update model metrics

## Architecture

```
dashboard/
├── main.py              # Main Streamlit application
├── config.py            # Configuration settings
├── utils.py             # Utility functions and classes
├── requirements.txt     # Python dependencies
└── components/          # Reusable UI components
```

### Key Components

1. **APIClient**: Handles all API communications
2. **ServiceMonitor**: Monitors external services
3. **FileManager**: File operations and model info
4. **DataProcessor**: Data processing and formatting

## Features in Detail

### Prediction Interface
- Support for single and batch predictions
- File upload validation
- Results visualization with topic distribution charts
- CSV export functionality

### Crawling Interface
- Real-time status updates
- Data statistics and visualizations
- Error handling and retry mechanisms
- Progress monitoring

### Training Interface
- Background training process
- Parameter configuration
- Training logs and status
- Model information display

### Monitoring Interface
- Service health checks
- External dashboard links
- System metrics visualization
- Performance monitoring

## Troubleshooting

### Common Issues

1. **API Not Available**
   - Ensure the API is running on localhost:8000
   - Check the API health endpoint
   - Verify network connectivity

2. **Module Import Errors**
   - Install missing dependencies
   - Check Python path configuration
   - Ensure virtual environment is activated

3. **File Upload Issues**
   - Verify file format (CSV, JSON)
   - Check file size limits
   - Ensure proper column names for CSV

4. **Training Not Starting**
   - Check model directory permissions
   - Verify training data availability
   - Monitor system resources

### Support

For issues and support:
1. Check the API logs for errors
2. Verify all services are running
3. Check the Streamlit logs in the terminal
4. Review the dashboard configuration

## Development

### Adding New Features

1. **New Pages**: Add to the option_menu in `main.py`
2. **API Endpoints**: Extend the APIClient class in `utils.py`
3. **Visualizations**: Use Plotly for interactive charts
4. **Configuration**: Add settings to `config.py`

### Code Structure

- Keep UI logic in `main.py`
- Business logic in `utils.py`
- Configuration in `config.py`
- Reusable components in `components/`

## License

This dashboard is part of the PTIIK Insight project and follows the same licensing terms.
