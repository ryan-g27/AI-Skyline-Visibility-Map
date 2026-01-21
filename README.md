# 🌟 AI for Star Viewing

A comprehensive machine learning project for predicting sky visibility and finding optimal stargazing locations. This project combines astronomical observation data, light pollution analysis, real-time weather data, and ML models to help astronomers and stargazers plan their observations.

## 📋 Project Overview

This project provides:
- **Machine Learning Models**: RandomForest regression models trained on real-world astronomical observations to predict sky quality
- **Interactive Web Application**: Streamlit-based map interface showing optimal stargazing locations with real-time cloudiness and moon data
- **Data Analysis Notebooks**: Comprehensive Jupyter notebooks for exploring and analyzing sky quality measurements
- **Light Pollution Mapping**: Image processing tools to extract light pollution indices from global maps

## 🎯 Key Features

- **Bortle Scale Prediction**: ML-powered predictions of sky quality (Bortle 1-9) based on location, elevation, cloud cover, and light pollution
- **Real-Time Weather Integration**: Live cloudiness and moon brightness data scraped from ClearOutside.com
- **Interactive Mapping**: Find optimal observation locations within customizable search radii
- **Global Coverage**: Analysis of worldwide astronomical observation data from the Globe at Night 2024 dataset
- **Light Pollution Analysis**: Extract pollution indices from satellite-based light pollution maps

## 🚀 Quick Start

### Prerequisites
- Python 3.8+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ryan-g27/AI-Skyline-Visibility-Map/tree/main
cd AI-Skyline-Visibility-Map
```

2. **Create and activate virtual environment**
```bash
python -m venv skyline
.\skyline\Scripts\Activate.ps1  # Windows PowerShell
# For Linux/Mac: source skyline/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Streamlit app**
```bash
streamlit run src/map_app/main.py
```

The app will open at **http://localhost:8501**

## 📊 Data Pipeline

1. **Raw Data**: Globe at Night 2024 observations (GaN2024.csv)
   - ~100k worldwide sky quality measurements
   - Features: Location, SQM reading, limiting magnitude, cloud cover, elevation

2. **Data Enrichment** (`make_GaN2024_Modified.py`)
   - Extract light pollution indices from satellite maps
   - Map RGB values to Bortle scale equivalents
   - Add geographical context

3. **Exploratory Analysis** (`explore_GaN2024.ipynb`)
   - Correlation analysis between features
   - Visualization of relationships
   - Feature importance evaluation

4. **Model Training** (`train_model_GaN2024.ipynb`)
   - RandomForest regression with hyperparameter tuning
   - Cross-validation and performance metrics
   - Model persistence with joblib

5. **Production Deployment** (Streamlit app)
   - Real-time predictions
   - Integration with weather APIs
   - Interactive visualization

## 🔬 Machine Learning Models

### Bortle Scale Predictor

**Algorithm**: RandomForestRegressor with optimized hyperparameters

**Features**:
- Elevation (meters)
- Cloud Cover (0-1 scale)
- SQM Reading (Sky Quality Meter magnitude per square arcsecond)
- Light Pollution Index (0-14 scale from satellite maps)

**Performance** (from training notebook):
- Test R²: 0.853
- Cross-validation score: ~0.85
- Mean Absolute Error: Low variance

**Feature Importance**:
1. SQM Reading (highest)
2. Light Pollution Index
3. Cloud Cover
4. Elevation

## 🗺️ Streamlit Map Application

The interactive web app provides:

### Features
- **Location Search**: Enter any address or coordinates
- **Real-Time Metrics**:
  - Sky Visibility (Bortle 1-9)
  - Cloudiness (0-100%)
  - Moon Brightness (phase and illumination)
- **Optimal Location Finder**: Discover best stargazing spots within 5-50 km radius
- **Interactive Map**: OpenStreetMap with location markers and search radius visualization

### Data Sources
- **Cloudiness**: ClearOutside.com (1-hour cache)
- **Moon Data**: ClearOutside.com (24-hour cache)
- **Bortle Predictions**: Local ML model (6-hour cache)

For detailed app documentation, see [src/map_app/README.md](src/map_app/README.md)

## 📓 Jupyter Notebooks

### 1. `explore_GaN2024.ipynb`
- Load and inspect Globe at Night data
- Correlation analysis between sky quality metrics
- Feature distribution visualizations
- Initial RandomForest modeling

### 2. `train_model_GaN2024.ipynb`
- Hyperparameter optimization with RandomizedSearchCV
- Model evaluation and validation
- Feature importance analysis
- Model export for production

### 3. `analyze_png_colors.py`
- Extract unique RGB values from light pollution maps
- Analyze color distributions
- Generate color palette visualizations
- Support for all continental map images

### 4. `make_GaN2024_Modified.py`
- Process raw Globe at Night CSV
- Map coordinates to light pollution indices
- Extract RGB values from continental PNG maps
- Generate enriched dataset for training

## 🛠️ Development

### Running Notebooks

```bash
# Activate environment
.\skyline\Scripts\Activate.ps1

# Start Jupyter
jupyter notebook notebooks/
```

### Running Tests

```bash
# Install test dependencies
pip install -r src/map_app/requirements.txt

# Run tests
pytest -q src/map_app/tests
```

### Training Models

```bash
jupyter notebook notebooks/train_model_GaN2024.ipynb
```

## 📦 Dependencies

See [requirements.txt](requirements.txt) for complete list.

## 🎯 Use Cases

1. **Amateur Astronomers**: Find optimal stargazing locations near you
2. **Astrophotographers**: Plan shoots with real-time weather and moon data
3. **Research**: Analyze global light pollution trends
4. **Education**: Demonstrate ML applications in astronomy
5. **Citizen Science**: Contribute observations to Globe at Night

## 🔄 Workflow Example

```bash
# 1. Activate environment
.\skyline\Scripts\Activate.ps1

# 2. Process raw data (if needed)
python notebooks/make_GaN2024_Modified.py

# 3. Explore data in notebook
jupyter notebook notebooks/explore_GaN2024.ipynb

# 4. Train ML model
python src/models/train_bortle_model.py

# 5. Launch web app
streamlit run src/map_app/main.py

# 6. Open browser to http://localhost:8501
# 7. Enter location and explore optimal stargazing sites!
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

### Notebook Kernel Issues
```bash
# Install ipykernel in the virtual environment
pip install ipykernel
python -m ipykernel install --user --name=skyline
```

### Map Not Displaying
- Check that streamlit-folium is installed
- Clear browser cache
- Try a different browser

### Web Scraping Failures
- The app includes fallback mechanisms
- Check internet connection
- ClearOutside.com may have changed structure (update parsers in weather_service.py)

## 📈 Future Enhancements

- [ ] Time-series predictions for future sky quality
- [ ] User accounts and observation history
- [ ] Mobile app version
- [ ] Integration with more weather APIs (OpenWeatherMap, Weatherstack)
- [ ] Deep learning models for improved predictions
- [ ] Historical sky quality trends and analysis
- [ ] Community observation sharing
- [ ] Export data to popular planetarium software
- [ ] Automated email alerts for optimal viewing conditions

## 🙏 Acknowledgments

- **Globe at Night**: International citizen science project providing sky quality data
- **ClearOutside.com**: Weather and astronomical data
- **Light Pollution Maps**: Satellite-based light pollution imagery
- **OpenStreetMap**: Mapping infrastructure
