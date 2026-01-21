"""Service to find nearby observation locations from CSV dataset.

This module provides functionality to search for actual observation locations
within a radius of a target point, using the GaN2024_Modified.csv dataset.
"""

import pandas as pd
import math
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def find_nearby_observation_locations(
    latitude: float,
    longitude: float,
    radius_km: float,
    csv_path: Optional[str] = None,
    top_n: int = 10
) -> List[Dict]:
    """
    Find actual observation locations near target coordinates from CSV dataset.
    
    Args:
        latitude: Target latitude
        longitude: Target longitude
        radius_km: Search radius in kilometers
        csv_path: Path to CSV file (optional, defaults to GaN2024_Modified.csv in assets)
        top_n: Maximum number of locations to return (default: 10)
    
    Returns:
        List of dictionaries with location info, sorted by distance (closest first).
        Each dictionary contains:
        - name: Location description (based on distance)
        - latitude: Location latitude
        - longitude: Location longitude
        - distance_km: Distance from target in km
        - light_pollution_index: Light pollution index value
        - limiting_mag: Limiting magnitude (naked eye star visibility)
        - cloud_cover: Cloud cover percentage
        - conditions: Brief description
        - bortle_score: (backward-compatible, same as light_pollution_index)
        - cloudiness_percent: (backward-compatible, same as cloud_cover)
        - moon_brightness: (backward-compatible, always 0)
    """
    try:
        # Default path to CSV in assets folder
        if csv_path is None:
            script_dir = Path(__file__).resolve().parent
            csv_path = str(script_dir.parent / "models" / "assets" / "GaN2024_Modified.csv")
        
        # Load the CSV
        logger.info(f"Loading observation data from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Calculate distances
        logger.info(f"Calculating distances from ({latitude}, {longitude})...")
        df['distance_km'] = df.apply(
            lambda row: haversine_distance(
                latitude, longitude, row['Latitude'], row['Longitude']
            ),
            axis=1
        )
        
        # Filter by distance
        nearby = df[df['distance_km'] <= radius_km].copy()
        
        logger.info(f"Found {len(nearby)} observation locations within {radius_km} km")
        
        if nearby.empty:
            return []
        
        # Select relevant columns
        columns_to_keep = [
            'Latitude', 'Longitude', 'distance_km',
            'LimitingMag', 'CloudCover', 'LightPollutionIndex'
        ]
        
        nearby = nearby[columns_to_keep].sort_values('distance_km')
        
        # Limit to top_n results
        nearby = nearby.head(top_n)
        
        # Convert to list of dictionaries matching optimal_locations format
        results: List[Dict] = []
        for idx, row in nearby.iterrows():
            distance = round(float(row['distance_km']), 2)
            location_dict = {
                'name': f"{distance} km away",
                'latitude': float(row['Latitude']),
                'longitude': float(row['Longitude']),
                'distance_km': distance,
                'light_pollution_index': float(row['LimitingMag']) if pd.notna(row['LimitingMag']) else None,
                'limiting_mag': float(row['LimitingMag']) if pd.notna(row['LimitingMag']) else None,
                'cloud_cover': int(row['CloudCover']) if pd.notna(row['CloudCover']) else None,
                # Backward-compatible fields used by UI components
                'bortle_score': float(row['LimitingMag']) if pd.notna(row['LimitingMag']) else None,
                'cloudiness_percent': int(row['CloudCover']) if pd.notna(row['CloudCover']) else 0,
                'moon_brightness': 0,
                'conditions': f"Observation location {distance} km from center",
            }
            results.append(location_dict)
        
        return results
        
    except Exception as e:
        logger.error(f"Error finding nearby observation locations: {e}")
        return []


def _print_results(results: List[Dict]) -> None:
    """Pretty-print nearby observation location results."""
    if not results:
        print("No observation locations found within the specified radius.")
        return

    for i, r in enumerate(results, start=1):
        print(f"\n[{i}] {r['name']}")
        print(f"  latitude: {r['latitude']}")
        print(f"  longitude: {r['longitude']}")
        print(f"  distance_km: {r['distance_km']}")
        print(f"  limiting_mag: {r['limiting_mag']}")
        print(f"  light_pollution_index: {r['light_pollution_index']}")
        print(f"  cloud_cover: {r['cloud_cover']}")


if __name__ == "__main__":
    # Review values near Washington DC area
    LAT = 38.92
    LON = -77.25
    RADIUS_KM = 20
    TOP_N = 10

    print("=" * 60)
    print(f"Nearby observation locations within {RADIUS_KM} km of ({LAT}, {LON})")
    print("=" * 60)

    results = find_nearby_observation_locations(LAT, LON, RADIUS_KM, top_n=TOP_N)
    print(f"\nTotal found: {len(results)}")
    _print_results(results)
