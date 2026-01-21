import pytest
from services import visibility_service
from models.bortle_predictor import BortlePredictor, get_sky_quality_description


def test_get_sky_visibility_returns_valid_data():
    """Test get_sky_visibility with actual ML model or fallback."""
    result = visibility_service.get_sky_visibility(40.730610, -73.935242)
    
    # Check required fields
    assert "bortle_scale" in result
    assert "visibility_score" in result
    assert "sky_quality" in result
    assert "confidence" in result
    assert "source" in result
    
    # Check types and valid ranges
    assert isinstance(result["bortle_scale"], int)
    assert 1 <= result["bortle_scale"] <= 9
    assert isinstance(result["visibility_score"], (int, float))
    assert 0 <= result["visibility_score"] <= 100
    assert result["source"] in ["ml_model", "heuristic", "fallback"]
    assert 0 <= result["confidence"] <= 1


def test_sky_quality_matches_bortle_scale():
    """Test that sky quality description matches Bortle scale."""
    result = visibility_service.get_sky_visibility(40.730610, -73.935242)
    bortle = result["bortle_scale"]
    quality = result["sky_quality"]
    
    # Should match the description from the model
    expected_quality = get_sky_quality_description(bortle)
    assert quality == expected_quality


def test_visibility_score_inverse_of_bortle():
    """Test that visibility score is calculated as (9 - bortle_scale) / 8 * 100."""
    result = visibility_service.get_sky_visibility(40.730610, -73.935242)
    bortle = result["bortle_scale"]
    visibility = result["visibility_score"]
    
    # Calculate expected visibility score
    expected_visibility = (9 - bortle) / 8 * 100
    assert abs(visibility - expected_visibility) < 0.1  # Allow small rounding difference


def test_bortle_predictor_heuristic():
    """Test BortlePredictor heuristic fallback method."""
    predictor = BortlePredictor()
    
    # Test heuristic on known regions
    nyc_bortle = predictor.predict_heuristic(40.730610, -73.935242)  # NYC
    assert 1 <= nyc_bortle <= 9
    
    # NYC should have higher light pollution (higher Bortle score)
    rural_bortle = predictor.predict_heuristic(43.0, -107.0)  # Rural Wyoming
    assert 1 <= rural_bortle <= 9
