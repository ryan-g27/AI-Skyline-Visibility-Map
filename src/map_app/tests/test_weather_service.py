import pytest
from services import weather_service


def test_get_cloudiness_returns_valid_data():
    """Test get_cloudiness with real network call to ClearOutside.com."""
    result = weather_service.get_cloudiness(40.730610, -73.935242)
    
    # Check required fields
    assert "cloudiness_percent" in result
    assert "forecast_description" in result
    assert "source" in result
    
    # Check types and valid ranges
    assert isinstance(result["cloudiness_percent"], int)
    assert 0 <= result["cloudiness_percent"] <= 100
    assert result["source"] in ["scraped", "fallback"]


def test_cloudiness_description_matches_value():
    """Test that cloudiness description matches the percentage value."""
    result = weather_service.get_cloudiness(40.730610, -73.935242)
    cloudiness = result["cloudiness_percent"]
    description = result["forecast_description"]
    
    # Verify description matches cloudiness range
    if cloudiness < 10:
        assert description == "Clear"
    elif cloudiness < 30:
        assert description == "Mostly clear"
    elif cloudiness < 50:
        assert description == "Partly cloudy"
    elif cloudiness < 70:
        assert description == "Mostly cloudy"
    else:
        assert description == "Overcast"


def test_get_moon_brightness_returns_valid_data():
    """Test get_moon_brightness with real network call to ClearOutside.com."""
    result = weather_service.get_moon_brightness(40.730610, -73.935242)
    
    # Check required fields
    assert "moon_phase" in result
    assert "illumination_percent" in result
    assert "source" in result
    
    # Check types and valid ranges
    assert isinstance(result["illumination_percent"], (int, float))
    assert 0 <= result["illumination_percent"] <= 100
    assert result["source"] in ["scraped", "fallback"]


def test_get_bortle_scale_returns_valid_data():
    """Test get_bortle_scale with real network call to ClearOutside.com."""
    result = weather_service.get_bortle_scale(40.730610, -73.935242)
    
    # Check required fields
    assert "bortle_scale" in result
    assert "magnitude" in result
    assert "brightness_mcd_m2" in result
    assert "artificial_brightness_ucd_m2" in result
    assert "source" in result
    
    # Check types and valid ranges
    assert isinstance(result["bortle_scale"], int)
    assert 1 <= result["bortle_scale"] <= 9
    assert result["source"] in ["scraped", "fallback"]
    assert result["source"] in ["scraped", "fallback"]
