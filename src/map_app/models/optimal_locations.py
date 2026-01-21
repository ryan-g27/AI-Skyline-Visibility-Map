"""Optimal location finder using PNG light pollution maps.

This module will analyze light pollution maps to find the best stargazing
locations within a given radius from a center point.
"""
from typing import List, Dict, Tuple, Optional
import math
import os
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# [lon_min, lat_min, lon_max, lat_max, width, height, filename]
CONTINENTS = {
    "North America": [-180, 7, -51, 75, 15480, 8160, 'NorthAmerica2024.png'],
    "South America": [-93, -57, -33, 14, 7200, 8520, 'SouthAmerica2024.png'],
    "Europe":        [-32, 34, 70, 75, 12240, 4920, 'Europe2024.png'],
    "Africa":        [-26, -36, 64, 38, 10800, 8800, 'Africa2024.png'],
    "Asia":          [60, 5, 180, 75, 14400, 8400, 'Asia2024.png'],
    "Australia":     [94, -48, 180, 8, 10320, 6720, 'Australia2024.png']
}

LIGHT_POLLUTION_SCALE = {
    (0, 0, 0): 0,
    (34, 34, 34): 1,
    (66, 66, 66): 1.5,
    (20, 47, 114): 2,
    (33, 84, 216): 2.5,
    (15, 87, 20): 3,
    (31, 161, 42): 3.5,
    (110, 100, 30): 4,
    (184, 166, 37): 4.5,
    (191, 100, 30): 5.0,
    (253, 150, 80): 5.5,
    (251, 90, 73): 6.0,
    (251, 153, 138): 6.5,
    (160, 160, 160): 7,
    (242, 242, 242): 7.5
}


class OptimalLocationFinder:
    """Find optimal stargazing locations using PNG light pollution maps."""
    
    def __init__(self):
        """Initialize the optimal location finder."""
        # Path to light pollution maps
        self.maps_dir = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "light_pollution_maps"
        )
        
        # Use shared color scale for all methods
        self.light_pollution_scale = LIGHT_POLLUTION_SCALE
        
        # Cache loaded maps by region name to avoid repeated disk reads
        self._map_cache: Dict[str, Tuple[np.ndarray, Dict[str, float]]] = {}
    
    def find_optimal_locations(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: int,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Find optimal stargazing locations within radius using PNG maps.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            top_n: Number of top locations to return
        
        Returns:
            List of dictionaries with location info (lat, lon, score, distance)
        
        Returns up to `top_n` locations that have lower light pollution than the
        center point. Returns an empty list if no better pixels are found (for
        example, if the entire search area is the same color).
        """
        region = self._get_region_info(center_lat, center_lon)
        if region is None:
            logger.warning("Coordinates (lat=%.4f, lon=%.4f) fall outside supported maps", center_lat, center_lon)
            return []

        map_array, region = self._load_map_for_region(center_lat, center_lon)

        # Determine center pixel pollution level
        center_x, center_y = self._latlon_to_pixel(center_lat, center_lon, region)
        center_rgb = tuple(int(v) for v in map_array[center_y, center_x])
        center_level = self._get_light_pollution_level(center_rgb)

        # Compute bounding box for the search area in lat/lon
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(center_lat))))

        search_lat_min = max(region["lat_min"], center_lat - lat_delta)
        search_lat_max = min(region["lat_max"], center_lat + lat_delta)
        search_lon_min = max(region["lon_min"], center_lon - lon_delta)
        search_lon_max = min(region["lon_max"], center_lon + lon_delta)

        # Convert bounding box to pixel coordinates
        x_min, y_min = self._latlon_to_pixel(search_lat_max, search_lon_min, region)
        x_max, y_max = self._latlon_to_pixel(search_lat_min, search_lon_max, region)

        x_min, x_max = int(min(x_min, x_max)), int(max(x_min, x_max))
        y_min, y_max = int(min(y_min, y_max)), int(max(y_min, y_max))

        # Guard against empty selections
        if x_min == x_max or y_min == y_max:
            return []

        # Build lat/lon grids for the search window
        x_range = np.arange(x_min, x_max + 1)
        y_range = np.arange(y_min, y_max + 1)

        lon_vals = region["lon_min"] + (x_range + 0.5) / region["width"] * (region["lon_max"] - region["lon_min"])
        lat_vals = region["lat_max"] - (y_range + 0.5) / region["height"] * (region["lat_max"] - region["lat_min"])

        lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

        # Slice image data for the region of interest
        window = map_array[y_min : y_max + 1, x_min : x_max + 1]

        # Compute distances and mask points within radius
        distances = self._haversine_grid(center_lat, center_lon, lat_grid, lon_grid)
        within_radius_mask = distances <= radius_km

        if not within_radius_mask.any():
            return []

        valid_y, valid_x = np.where(within_radius_mask)
        valid_colors = window[valid_y, valid_x]

        # Map colors to pollution levels
        valid_levels = np.array([
            self._get_light_pollution_level(tuple(int(v) for v in rgb)) for rgb in valid_colors
        ])
        valid_distances = distances[valid_y, valid_x]
        valid_lats = lat_grid[valid_y, valid_x]
        valid_lons = lon_grid[valid_y, valid_x]

        # Keep only pixels that are better than center
        better_mask = valid_levels < center_level
        if not better_mask.any():
            return []

        # Sort by pollution level first, then by proximity
        order = np.lexsort((valid_distances[better_mask], valid_levels[better_mask]))
        selected_indices = np.nonzero(better_mask)[0][order][:top_n]

        results: List[Dict[str, float]] = []
        for rank, idx in enumerate(selected_indices, start=1):
            results.append(
                {
                    "name": f"Low-light spot #{rank}",
                    "latitude": float(valid_lats[idx]),
                    "longitude": float(valid_lons[idx]),
                    "distance_km": float(valid_distances[idx]),
                    "light_pollution_index": float(round(valid_levels[idx], 2)),
                    # Backward-compatible field used by UI components
                    "bortle_score": float(round(valid_levels[idx], 2)),
                    "cloudiness_percent": 0,
                    "moon_brightness": 0,
                    "conditions": "Lower light pollution compared to center",
                }
            )

        return results
    
    def _load_map_for_region(self, latitude: float, longitude: float) -> np.ndarray:
        """
        Load the appropriate PNG map for the given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            Numpy array of the image
        
        """
        region = self._get_region_info(latitude, longitude)
        if region is None:
            raise ValueError("Coordinates fall outside supported map regions")

        cache_key = region["name"]
        if cache_key in self._map_cache:
            return self._map_cache[cache_key]

        map_path = os.path.join(self.maps_dir, region["filename"])
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Map file not found: {map_path}")

        image = Image.open(map_path).convert("RGB")
        map_array = np.array(image)

        # Sanity check for expected dimensions
        expected_height, expected_width = int(region["height"]), int(region["width"])
        if map_array.shape[0] != expected_height or map_array.shape[1] != expected_width:
            logger.warning(
                "Map dimensions mismatch for %s: expected (%d, %d) got %s",
                cache_key,
                expected_height,
                expected_width,
                map_array.shape,
            )

        self._map_cache[cache_key] = (map_array, region)
        return map_array, region
    
    def _latlon_to_pixel(
        self,
        latitude: float,
        longitude: float,
        map_bounds: Tuple[float, float, float, float],
        image_shape: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Convert lat/lon coordinates to pixel coordinates on the map.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            map_bounds: (min_lat, max_lat, min_lon, max_lon) of the map
            image_shape: (height, width) of the image
        
        Returns:
            (x, y) pixel coordinates
        
        """
        lon_min = region["lon_min"]
        lon_max = region["lon_max"]
        lat_min = region["lat_min"]
        lat_max = region["lat_max"]
        width = region["width"]
        height = region["height"]

        x = (longitude - lon_min) / (lon_max - lon_min) * (width - 1)
        y = (lat_max - latitude) / (lat_max - lat_min) * (height - 1)

        x_clamped = min(max(int(round(x)), 0), int(width) - 1)
        y_clamped = min(max(int(round(y)), 0), int(height) - 1)
        return x_clamped, y_clamped
    
    def _get_light_pollution_level(self, rgb: Tuple[int, int, int]) -> int:
        """
        Get light pollution level from RGB color.
        
        Args:
            rgb: RGB tuple (r, g, b)
        
        Returns:
            Light pollution level (0-7, lower is better)
        """
        # Find closest matching color in scale
        min_distance = float('inf')
        closest_level = 4  # Default to middle value
        
        for color, level in self.light_pollution_scale.items():
            distance = sum((a - b) ** 2 for a, b in zip(rgb, color))
            if distance < min_distance:
                min_distance = distance
                closest_level = level
        
        return closest_level

    def get_light_pollution_at(self, latitude: float, longitude: float) -> float:
        """Return light pollution level at a specific coordinate."""
        map_array, region = self._load_map_for_region(latitude, longitude)
        x, y = self._latlon_to_pixel(latitude, longitude, region)
        rgb = tuple(int(v) for v in map_array[y, x])
        return float(self._get_light_pollution_level(rgb))

    def _get_region_info(self, latitude: float, longitude: float) -> Optional[Dict[str, float]]:
        """Return region metadata for given coordinates, or None if not covered."""
        for name, values in CONTINENTS.items():
            lon_min, lat_min, lon_max, lat_max, width, height, filename = values
            if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
                return {
                    "name": name,
                    "lon_min": lon_min,
                    "lat_min": lat_min,
                    "lon_max": lon_max,
                    "lat_max": lat_max,
                    "width": width,
                    "height": height,
                    "filename": filename,
                }
        return None

    def _pixel_to_latlon(self, x: int, y: int, region: Dict[str, float]) -> Tuple[float, float]:
        """Convert pixel coordinates back to latitude and longitude."""
        lon = region["lon_min"] + (x + 0.5) / region["width"] * (region["lon_max"] - region["lon_min"])
        lat = region["lat_max"] - (y + 0.5) / region["height"] * (region["lat_max"] - region["lat_min"])
        return float(lat), float(lon)

    def _haversine_grid(self, lat0: float, lon0: float, lat_grid: np.ndarray, lon_grid: np.ndarray) -> np.ndarray:
        """Vectorized haversine distance in kilometers for a grid of coordinates."""
        radius_earth_km = 6371.0

        lat0_rad = math.radians(lat0)
        lon0_rad = math.radians(lon0)

        lat_grid_rad = np.radians(lat_grid)
        lon_grid_rad = np.radians(lon_grid)

        delta_lat = lat_grid_rad - lat0_rad
        delta_lon = lon_grid_rad - lon0_rad

        a = np.sin(delta_lat / 2) ** 2 + np.cos(lat0_rad) * np.cos(lat_grid_rad) * np.sin(delta_lon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return radius_earth_km * c
