"""
Map utilities for creating and managing interactive maps.
"""

import folium
import streamlit as st
from typing import Tuple, List, Dict, Any


def create_base_map(
    center_latitude: float, center_longitude: float, zoom_level: int = 12
) -> folium.Map:
    """
    Create a base folium map centered at given coordinates.

    Args:
        center_latitude: Latitude of map center
        center_longitude: Longitude of map center
        zoom_level: Initial zoom level (default: 12)

    Returns:
        folium.Map: Configured folium map object
    """
    base_map = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=zoom_level,
        tiles="OpenStreetMap",
    )
    return base_map


def add_center_marker(
    map_obj: folium.Map, latitude: float, longitude: float, location_name: str
) -> folium.Map:
    """
    Add a marker at the center of the map.

    Args:
        map_obj: Folium map object
        latitude: Marker latitude
        longitude: Marker longitude
        location_name: Name to display in popup

    Returns:
        folium.Map: Map with center marker added
    """
    folium.Marker(
        location=[latitude, longitude],
        popup=f"<b>📍 {location_name}</b><br>Lat: {latitude:.4f}<br>Lon: {longitude:.4f}",
        tooltip=location_name,
        icon=folium.Icon(color="red", icon="location-dot", prefix="fa"),
    ).add_to(map_obj)
    return map_obj


def add_radius_circle(
    map_obj: folium.Map, latitude: float, longitude: float, radius_km: float
) -> folium.Map:
    """
    Add a circle to the map representing search radius.

    Args:
        map_obj: Folium map object
        latitude: Circle center latitude
        longitude: Circle center longitude
        radius_km: Radius in kilometers

    Returns:
        folium.Map: Map with radius circle added
    """
    # Convert kilometers to meters for folium
    radius_meters = radius_km * 1000

    folium.Circle(
        location=[latitude, longitude],
        radius=radius_meters,
        popup=f"Search Radius: {radius_km} km",
        color="blue",
        fill=True,
        fillColor="blue",
        fillOpacity=0.1,
        weight=2,
    ).add_to(map_obj)
    return map_obj


def add_optimal_location_markers(
    map_obj: folium.Map, locations: List[Dict[str, Any]]
) -> folium.Map:
    """
    Add markers for optimal observation locations to the map.

    Args:
        map_obj: Folium map object
        locations: List of location dictionaries with lat, lon, name, conditions

    Returns:
        folium.Map: Map with optimal location markers added
    """
    for idx, loc in enumerate(locations, 1):
        # Color code based on Bortle score
        pollution_value = loc.get("light_pollution_index", loc.get("bortle_score", 5))
        if pollution_value <= 2:
            icon_color = "green"
        elif pollution_value <= 4:
            icon_color = "lightgreen"
        else:
            icon_color = "orange"

        popup_text = f"""
        <b>{idx}. {loc.get('name', 'Unknown')}</b><br>
        Light Pollution: {pollution_value}<br>
        Distance: {loc.get('distance_km', 0):.1f} km<br>
        Cloudiness: {loc.get('cloudiness_percent', 0)}%<br>
        Conditions: {loc.get('conditions', 'Unknown')}
        """

        folium.Marker(
            location=[loc.get("latitude"), loc.get("longitude")],
            popup=folium.Popup(popup_text, max_width=200),
            tooltip=f"{idx}. {loc.get('name', 'Unknown')}",
            icon=folium.Icon(color=icon_color, icon="star", prefix="fa"),
        ).add_to(map_obj)

    return map_obj


def geocode_location(location_str: str) -> Tuple[float, float, str]:
    """
    Convert location string to coordinates using geopy.

    Args:
        location_str: Address or location name string

    Returns:
        Tuple[float, float, str]: (latitude, longitude, location_name)
    """
    try:
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="star_observation_map")
        location = geolocator.geocode(location_str)

        if location:
            return (location.latitude, location.longitude, location_str)
        else:
            st.warning(f"Location '{location_str}' not found. Using default.")
            from config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_LOCATION_NAME

            return (DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_LOCATION_NAME)
    except Exception as e:
        st.error(f"Error geocoding location: {str(e)}")
        from config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_LOCATION_NAME

        return (DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_LOCATION_NAME)
