"""Sky visibility service for predicting Bortle scale and sky quality."""
import streamlit as st
import logging
from typing import Dict
from models.bortle_predictor import BortlePredictor, get_sky_quality_description

logger = logging.getLogger(__name__)


@st.cache_data(ttl=21600)
def get_sky_visibility(latitude: float, longitude: float) -> Dict:
    """
    Predict sky visibility and Bortle scale.
    
    Uses ML-based prediction with fallback to heuristics.
    Cache expires after 6 hours (21600 seconds).
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Dictionary with bortle_scale, visibility_score, and sky_quality
    """
    try:
        # Initialize predictor
        predictor = BortlePredictor()
        
        # Try ML prediction first
        try:
            bortle_scale = predictor.predict(latitude, longitude)
            source = "ml_model"
            confidence = 0.75
        except Exception as ml_error:
            logger.warning(f"ML prediction failed: {ml_error}, using heuristic fallback")
            bortle_scale = predictor.predict_heuristic(latitude, longitude)
            source = "heuristic"
            confidence = 0.60
        
        # Calculate visibility score (inverse of Bortle, normalized to 0-100)
        visibility_score = (9 - bortle_scale) / 8 * 100
        sky_quality = get_sky_quality_description(bortle_scale)
        
        return {
            "bortle_scale": bortle_scale,
            "visibility_score": round(visibility_score, 1),
            "sky_quality": sky_quality,
            "confidence": confidence,
            "source": source
        }
    
    except Exception as e:
        logger.error(f"Error predicting sky visibility: {e}")
        # Final fallback with low confidence
        return {
            "bortle_scale": 5,
            "visibility_score": 50.0,
            "sky_quality": "Suburban sky",
            "confidence": 0.50,
            "source": "fallback"
        }


if __name__ == "__main__":
    """Debug script to test visibility service functions."""
    import json
    
    # Test coordinates: Times Square, NYC
    latitude = 40.730610
    longitude = -73.935242
    
    print("=" * 60)
    print(f"Testing Visibility Service (NYC: {latitude}, {longitude})")
    print("=" * 60)
    
    # Test sky visibility
    print("\n🌌 Testing get_sky_visibility()...")
    visibility_result = get_sky_visibility(latitude, longitude)
    print(json.dumps(visibility_result, indent=2))
    
    # Also test the Bortle predictor heuristic
    print("\n📊 Testing BortlePredictor heuristic...")
    from models.bortle_predictor import BortlePredictor
    predictor = BortlePredictor()
    heuristic_bortle = predictor.predict_heuristic(latitude, longitude)
    print(f"Heuristic Bortle Scale: {heuristic_bortle}")
    print(f"Sky Quality: {get_sky_quality_description(heuristic_bortle)}")
    
    print("\n" + "=" * 60)
    print("✅ Visibility service debugging complete!")
    print("=" * 60)
