"""
Configuration and constants for the Streamlit Map Application.
"""

# Map Configuration
DEFAULT_LATITUDE = 40.7128
DEFAULT_LONGITUDE = -74.0060
DEFAULT_LOCATION_NAME = "New York City"
DEFAULT_ZOOM_LEVEL = 10

# Radius Options (in kilometers)
RADIUS_OPTIONS = {
    "5 km": 5,
    "10 km": 10,
    "20 km": 20,
    "50 km": 50,
}
DEFAULT_RADIUS = 5  # km

# Mock Data for Optimal Coordinates
MOCK_OPTIMAL_LOCATIONS = [
    {
        "name": "1. 5.2 kms away",
        "latitude": 40.7580,
        "longitude": -73.9855,
        "distance_km": 5.2,
        "bortle_score": 1,
        "cloudiness_percent": 10,
        "moon_brightness": 20,
        "conditions": "Clear Skies",
    },
    {
        "name": "2. 8.7 kms away",
        "latitude": 40.7489,
        "longitude": -73.9680,
        "distance_km": 8.7,
        "bortle_score": 2,
        "cloudiness_percent": 25,
        "moon_brightness": 45,
        "conditions": "Partly Cloudy",
    },
    {
        "name": "3. 12.1 kms away",
        "latitude": 40.7614,
        "longitude": -73.9776,
        "distance_km": 12.1,
        "bortle_score": 3,
        "cloudiness_percent": 40,
        "moon_brightness": 70,
        "conditions": "Moon Bright",
    },
]

# UI Configuration
PAGE_TITLE = "AI Skyline Visibility Map"
PAGE_ICON = "🌟"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
