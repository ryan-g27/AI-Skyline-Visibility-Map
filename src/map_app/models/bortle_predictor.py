"""Bortle scale prediction model using RandomForestRegressor."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import logging
import streamlit as st

logger = logging.getLogger(__name__)


class BortlePredictor:
    """Predict Bortle scale from geographic coordinates using trained ML model."""
    
    def __init__(self):
        """Initialize the predictor by loading the trained model."""
        self.model = None
        self._load_model()
    
    @st.cache_resource
    def _load_model(_self) -> RandomForestRegressor:
        """
        Load a pre-trained RandomForestRegressor for Bortle scale prediction.
        
        The model should be trained and saved using:
            python src/models/train_bortle_model.py
        
        Returns:
            Trained RandomForestRegressor model loaded from disk
        
        Raises:
            FileNotFoundError: If the model file does not exist
        """
        # Construct path to the model file
        # Navigate from this file (models/bortle_predictor.py) to assets/bortle_model.joblib
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "assets", "bortle_model.joblib")
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Bortle scale model not found at {model_path}\n"
                "Please train the model first by running:\n"
                "  python src/models/train_bortle_model.py"
            )
        
        # Load the model
        model = joblib.load(model_path)
        logger.info(f"Loaded pre-trained Bortle scale model from {model_path}")
        return model
    
    def predict(self, latitude: float, longitude: float) -> int:
        """
        Predict Bortle scale based on geographic location.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        
        Returns:
            Predicted Bortle scale (1-9)
        """
        try:
            if self.model is None:
                self.model = self._load_model()
            
            # Prepare input features
            features = np.array([[latitude, longitude]])
            
            # Predict Bortle scale
            prediction = self.model.predict(features)[0]
            
            # Ensure prediction is within valid range [1-9]
            bortle_scale = max(1, min(9, round(prediction)))
            
            logger.debug(f"ML prediction for ({latitude}, {longitude}): {bortle_scale}")
            return bortle_scale
        
        except Exception as e:
            logger.warning(f"Error in ML prediction: {e}")
            raise
    
    def predict_heuristic(self, latitude: float, longitude: float) -> int:
        """
        Fallback heuristic-based Bortle scale prediction.
        
        Used when ML model fails or for comparison.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        
        Returns:
            Predicted Bortle scale (1-9)
        """
        abs_lat = abs(latitude)
        
        # Base estimate on latitude
        if abs_lat < 30:  # Tropical/subtropical - often urban
            bortle = 7
        elif abs_lat < 45:  # Temperate - mixed
            bortle = 5
        else:  # High latitude - often rural
            bortle = 3
        
        # Adjust based on major population center regions
        # North America East Coast
        if -100 < longitude < -70 and 25 < latitude < 50:
            bortle = min(bortle + 2, 9)
        
        # Western Europe
        elif 0 < longitude < 20 and 35 < latitude < 60:
            bortle = min(bortle + 2, 9)
        
        # East Asia
        elif 95 < longitude < 145 and 20 < latitude < 50:
            bortle = min(bortle + 1, 9)
        
        # Australia
        elif 110 < longitude < 160 and -45 < latitude < -10:
            bortle = max(bortle - 1, 1)
        
        # Adjust slightly for extreme latitudes
        if abs_lat > 70:
            bortle = max(bortle - 1, 1)
        
        return max(1, min(9, bortle))


def get_sky_quality_description(bortle_scale: int) -> str:
    """Get human-readable sky quality description for Bortle scale."""
    descriptions = {
        1: "Excellent dark-sky site",
        2: "Typical truly dark site",
        3: "Rural sky",
        4: "Rural/suburban transition",
        5: "Suburban sky",
        6: "Bright suburban sky",
        7: "Suburban/urban transition",
        8: "City sky",
        9: "Inner-city sky",
    }
    return descriptions.get(bortle_scale, "Unknown")
