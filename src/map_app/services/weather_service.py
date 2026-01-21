"""Weather service for fetching cloudiness and moon brightness data."""
import streamlit as st
from datetime import datetime
import re
from bs4 import BeautifulSoup
import httpx
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ClearOutsideWeatherFetcher:
    """Fetch and cache weather data from ClearOutside.com with single HTTP call."""
    
    def __init__(self, latitude: float, longitude: float):
        """
        Initialize fetcher and fetch data from ClearOutside.com.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.soup: Optional[BeautifulSoup] = None
        self._fetch_page()
    
    def _fetch_page(self) -> None:
        """Fetch the forecast page from ClearOutside.com."""
        try:
            url = f"https://clearoutside.com/forecast/{self.latitude:.6f}/{self.longitude:.6f}"
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"Successfully fetched ClearOutside forecast for ({self.latitude}, {self.longitude})")
        except Exception as e:
            logger.warning(f"Error fetching ClearOutside page: {e}")
            self.soup = None
    
    def get_cloudiness(self) -> Dict:
        """
        Extract cloudiness percentage from cached page.
        
        Returns:
            Dictionary with cloudiness_percent, description, and source
        """
        if self.soup is None:
            return self._fallback_cloudiness()
        
        try:
            cloudiness = self._extract_cloudiness_percent()
            description = self._get_cloud_description(cloudiness)
            
            return {
                "cloudiness_percent": cloudiness,
                "forecast_description": description,
                "source": "scraped"
            }
        except Exception as e:
            logger.error(f"Error extracting cloudiness: {e}")
            return self._fallback_cloudiness()
    
    def get_moon_brightness(self) -> Dict:
        """
        Extract moon phase and illumination from cached page.
        
        Returns:
            Dictionary with moon_phase, illumination_percent, rise/set times
        """
        if self.soup is None:
            return self._fallback_moon_data(datetime.utcnow())
        
        try:
            moon_data = self._extract_moon_data()
            return {**moon_data, "source": "scraped"}
        except Exception as e:
            logger.error(f"Error extracting moon data: {e}")
            return {**self._fallback_moon_data(datetime.utcnow()), "source": "fallback"}
    
    def get_bortle_scale(self) -> Dict:
        """
        Extract Bortle scale and light pollution data from cached page.
        
        Returns:
            Dictionary with bortle_scale, magnitude, brightness, and artificial_brightness
        """
        if self.soup is None:
            return self._fallback_bortle()
        
        try:
            bortle_data = self._extract_bortle_data()
            return {**bortle_data, "source": "scraped"}
        except Exception as e:
            logger.error(f"Error extracting Bortle data: {e}")
            return self._fallback_bortle()
    
    def _extract_cloudiness_percent(self) -> int:
        """Extract cloudiness percentage from HTML."""
        # Look for "Total Clouds" rows in forecast detail
        cloud_elements = self.soup.find_all(string=re.compile(r'cloud', re.IGNORECASE))
        
        for element in cloud_elements:
            parent = element.parent
            if parent:
                text = parent.get_text()
                percent_match = re.search(r'(\d+)\s*%', text)
                if percent_match:
                    value = int(percent_match.group(1))
                    if 0 <= value <= 100:
                        return value
        
        # Alternative: Look for forecast table cells
        forecast_cells = self.soup.find_all(['td', 'div'], class_=re.compile(r'cloud|forecast', re.IGNORECASE))
        for cell in forecast_cells:
            text = cell.get_text()
            percent_match = re.search(r'(\d+)\s*%', text)
            if percent_match:
                value = int(percent_match.group(1))
                if 0 <= value <= 100:
                    return value
        
        return 50  # Default if extraction fails
    
    def _extract_moon_data(self) -> Dict:
        """Extract moon phase and illumination from HTML."""
        illumination = 50.0
        phase = "Unknown"
        rise_time = None
        set_time = None
        
        # Find moon div with class "fc_moon"
        moon_div = self.soup.find('div', class_='fc_moon')
        if moon_div:
            # Extract moon phase
            phase_span = moon_div.find('span', class_='fc_moon_phase')
            if phase_span:
                phase = phase_span.get_text(strip=True)
            
            # Extract illumination percentage
            percent_span = moon_div.find('span', class_='fc_moon_percentage')
            if percent_span:
                percent_text = percent_span.get_text(strip=True)
                percent_match = re.search(r'(\d+)\s*%', percent_text)
                if percent_match:
                    illumination = float(percent_match.group(1))
            
            # Extract rise/set times
            riseset_span = moon_div.find('span', class_='fc_moon_riseset')
            if riseset_span:
                riseset_text = riseset_span.get_text()
                # Format: "08:01  16:44" or similar
                time_matches = re.findall(r'(\d{1,2}):(\d{2})', riseset_text)
                if len(time_matches) >= 2:
                    h1, m1 = time_matches[0]
                    h2, m2 = time_matches[1]
                    rise_time = f"{h1}:{m1}:00"
                    set_time = f"{h2}:{m2}:00"
        
        return {
            "moon_phase": phase,
            "illumination_percent": round(illumination, 1),
            "moon_rise_time": rise_time,
            "moon_set_time": set_time,
        }
    
    def _extract_bortle_data(self) -> Dict:
        """Extract Bortle scale and light pollution metrics from HTML."""
        # Look for span with class "btn btn-primary btn-bortle-X"
        bortle_span = self.soup.find('span', class_=re.compile(r'btn-bortle-\d'))
        
        bortle_scale = 5  # Default
        magnitude = 0.0
        brightness_mcd = 0.0
        artificial_brightness = 0.0
        
        if bortle_span:
            # Extract Bortle class number
            classes = bortle_span.get('class', [])
            for cls in classes:
                match = re.search(r'btn-bortle-(\d)', cls)
                if match:
                    bortle_scale = int(match.group(1))
                    break
            
            # Extract all strong tags which contain the metrics
            span_text = bortle_span.get_text()
            
            # Extract magnitude: "17.53 Magnitude"
            magnitude_match = re.search(r'(\d+\.?\d*)\s+Magnitude', span_text)
            if magnitude_match:
                magnitude = float(magnitude_match.group(1))
            
            # Extract brightness in mcd/m²: "10.52 mcd/m²"
            brightness_match = re.search(r'(\d+\.?\d*)\s*mcd/m', span_text)
            if brightness_match:
                brightness_mcd = float(brightness_match.group(1))
            
            # Extract artificial brightness: "10349.17 μcd/m²"
            artificial_match = re.search(r'(\d+\.?\d*)\s*μcd/m', span_text)
            if artificial_match:
                artificial_brightness = float(artificial_match.group(1))
        
        return {
            "bortle_scale": bortle_scale,
            "magnitude": round(magnitude, 2),
            "brightness_mcd_m2": round(brightness_mcd, 2),
            "artificial_brightness_ucd_m2": round(artificial_brightness, 2),
        }
    
    @staticmethod
    def _get_cloud_description(cloudiness: int) -> str:
        """Convert cloudiness percentage to description."""
        if cloudiness < 10:
            return "Clear"
        elif cloudiness < 30:
            return "Mostly clear"
        elif cloudiness < 50:
            return "Partly cloudy"
        elif cloudiness < 70:
            return "Mostly cloudy"
        else:
            return "Overcast"
    
    @staticmethod
    def _fallback_cloudiness() -> Dict:
        """Return fallback cloudiness data."""
        hour = datetime.utcnow().hour
        cloudiness = 40 if 6 <= hour <= 18 else 30
        return {
            "cloudiness_percent": cloudiness,
            "forecast_description": ClearOutsideWeatherFetcher._get_cloud_description(cloudiness),
            "source": "fallback"
        }
    
    @staticmethod
    def _fallback_moon_data(time: datetime) -> Dict:
        """Calculate moon data using simple lunar cycle approximation."""
        known_new_moon = datetime(2024, 1, 11)
        lunar_cycle = 29.53
        
        days_since = (time - known_new_moon).days % lunar_cycle
        phase_fraction = days_since / lunar_cycle
        
        illumination = abs(2 * phase_fraction - 1) * 100
        if phase_fraction > 0.5:
            illumination = 100 - illumination
        
        # Determine moon phase
        if illumination < 1:
            phase = "New Moon"
        elif illumination < 25:
            phase = "Waxing Crescent"
        elif illumination < 45:
            phase = "First Quarter"
        elif illumination < 55:
            phase = "Waxing Gibbous"
        elif illumination < 75:
            phase = "Full Moon"
        elif illumination < 95:
            phase = "Waning Gibbous"
        elif illumination < 99:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"
        
        return {
            "moon_phase": phase,
            "illumination_percent": round(illumination, 1),
            "moon_rise_time": None,
            "moon_set_time": None,
        }
    
    @staticmethod
    def _fallback_bortle() -> Dict:
        """Return fallback Bortle data."""
        return {
            "bortle_scale": 5,
            "magnitude": 0.0,
            "brightness_mcd_m2": 0.0,
            "artificial_brightness_ucd_m2": 0.0,
        }


@st.cache_resource
def get_weather_fetcher(latitude: float, longitude: float) -> ClearOutsideWeatherFetcher:
    """
    Get or create cached weather fetcher instance.
    
    Uses @st.cache_resource to ensure only one HTTP call per coordinate pair,
    even when multiple public functions request different metrics.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        ClearOutsideWeatherFetcher instance (cached by coordinates)
    """
    return ClearOutsideWeatherFetcher(latitude, longitude)


@st.cache_data(ttl=3600)
def get_cloudiness(latitude: float, longitude: float) -> Dict:
    """
    Get cloudiness percentage for a location (single web call).
    
    Reuses cached ClearOutsideWeatherFetcher instance.
    Cache expires after 1 hour (3600 seconds).
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Dictionary with cloudiness_percent and forecast_description
    """
    fetcher = get_weather_fetcher(latitude, longitude)
    return fetcher.get_cloudiness()


@st.cache_data(ttl=86400)
def get_moon_brightness(latitude: float, longitude: float) -> Dict:
    """
    Get moon brightness and phase information (single web call).
    
    Reuses cached ClearOutsideWeatherFetcher instance.
    Cache expires after 24 hours (86400 seconds).
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Dictionary with moon_phase, illumination_percent, and rise/set times
    """
    fetcher = get_weather_fetcher(latitude, longitude)
    return fetcher.get_moon_brightness()


@st.cache_data(ttl=21600)
def get_bortle_scale(latitude: float, longitude: float) -> Dict:
    """
    Get Bortle scale and light pollution metrics (single web call).
    
    Reuses cached ClearOutsideWeatherFetcher instance.
    Cache expires after 6 hours (21600 seconds).
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Dictionary with bortle_scale, magnitude, brightness measurements
    """
    fetcher = get_weather_fetcher(latitude, longitude)
    return fetcher.get_bortle_scale()


if __name__ == "__main__":
    """Debug script to test weather service functions."""
    import json
    
    # Test coordinates: Times Square, NYC
    latitude = 40.730610
    longitude = -73.935242
    
    print("=" * 60)
    print(f"Testing Weather Service (NYC: {latitude}, {longitude})")
    print("=" * 60)
    
    # Create fetcher - single web call
    print("\n📡 Fetching data from ClearOutside.com (single call)...")
    fetcher = ClearOutsideWeatherFetcher(latitude, longitude)
    
    # Test cloudiness
    print("\n☁️ Cloudiness Data:")
    cloudiness_result = fetcher.get_cloudiness()
    print(json.dumps(cloudiness_result, indent=2))
    
    # Test moon brightness
    print("\n🌙 Moon Brightness Data:")
    moon_result = fetcher.get_moon_brightness()
    print(json.dumps(moon_result, indent=2))
    
    # Test Bortle scale
    print("\n🌌 Bortle Scale & Light Pollution Data:")
    bortle_result = fetcher.get_bortle_scale()
    print(json.dumps(bortle_result, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ Weather service debugging complete!")
    print("=" * 60)
