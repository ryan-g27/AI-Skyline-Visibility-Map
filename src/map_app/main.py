"""
Main Streamlit application for AI Skyline Visibility Map.

This application displays an interactive map for viewing star observation locations
with metrics like Bortle score, cloudiness, and moon brightness.
"""

import streamlit as st
import pandas as pd
from typing import Tuple

# Import configuration and components
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_ZOOM_LEVEL,
    DEFAULT_RADIUS,
    RADIUS_OPTIONS,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)
from utils.map_utils import (
    create_base_map,
    add_center_marker,
    add_radius_circle,
    add_optimal_location_markers,
    geocode_location,
)
from components.sidebar import render_sidebar_metrics
from components.map_display import render_map, render_optimal_locations_panel
from services.nearby_locations_service import find_nearby_observation_locations


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

# Custom CSS for better layout
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "latitude" not in st.session_state:
        st.session_state.latitude = DEFAULT_LATITUDE
    if "longitude" not in st.session_state:
        st.session_state.longitude = DEFAULT_LONGITUDE
    if "location_name" not in st.session_state:
        st.session_state.location_name = DEFAULT_LOCATION_NAME
    if "first_search_done" not in st.session_state:
        st.session_state.first_search_done = False
    if "selected_radius" not in st.session_state:
        st.session_state.selected_radius = DEFAULT_RADIUS


def get_location_metrics(latitude: float, longitude: float, location_name: str) -> dict:
    """Compute light pollution metrics for the current location."""
    # Use default placeholder value until we have actual location data
    pollution_level = 7.0

    return {
        "latitude": latitude,
        "longitude": longitude,
        "location_name": location_name,
        "light_pollution_index": pollution_level,
        "bortle_score": pollution_level,
        "cloudiness_percent": 27,
        "moon_brightness": 4,
    }


def get_optimal_locations_for_radius(radius_km: int, max_locations: int = 5) -> list:
    """Find nearby observation locations from CSV dataset within the given radius."""
    try:
        return find_nearby_observation_locations(
            st.session_state.latitude,
            st.session_state.longitude,
            radius_km,
            top_n=max_locations,
        )
    except Exception as exc:  # noqa: BLE001 - surface error to UI
        st.error(f"Failed to find nearby observation locations: {exc}")
        return []


def main() -> None:
    """Main application function."""
    # Initialize session state
    initialize_session_state()

    # Header with location input
    st.markdown("# 🌟 AI Skyline Visibility Map")

    # Location search form
    col1, col2 = st.columns([4, 1])
    
    with col1:
        with st.form(key="location_form", clear_on_submit=False):
            location_input = st.text_input(
                label="📍 Enter Location",
                placeholder="Enter address or coordinates (e.g., 'New York' or '40.7128,-74.0060')",
                value=st.session_state.location_name,
                key="location_input",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("🔍 Search", use_container_width=True)
            
            if submitted and location_input:
                # Geocode the location
                lat, lon, name = geocode_location(location_input)
                st.session_state.latitude = lat
                st.session_state.longitude = lon
                st.session_state.location_name = name
                st.session_state.first_search_done = True
                st.rerun()

    with col2:
        st.button("📍 Use My Location", use_container_width=True, disabled=True, help="Coming soon")
        
        st.selectbox(
            "Select Radius:",
            options=RADIUS_OPTIONS.keys(),
            format_func=lambda x: x,
            key="radius_selector",
            on_change=lambda: st.session_state.update({"selected_radius": RADIUS_OPTIONS[st.session_state.radius_selector]})
        )

    st.markdown("---")

    # Main layout: Left sidebar + Main content (map + bottom panel)
    # Only show sidebar after first search
    if st.session_state.first_search_done:
        render_sidebar_metrics(
            get_location_metrics(
                st.session_state.latitude,
                st.session_state.longitude,
                st.session_state.location_name,
            )
        )
    else:
        # Show a welcome message in the sidebar
        with st.sidebar:
            st.markdown("## 👋 Welcome!")
            st.info(
                "🔍 **Get Started:**\n\n"
                "1. Enter a location in the search box above\n"
                "2. Click **Search** or press Enter\n"
                "3. Or click **Use My Location** to use GPS\n\n"
                "The map and metrics will appear after your first search!"
            )

    # Main content area
    st.markdown("### 🗺️ Interactive Map")

    # Create map
    map_obj = create_base_map(
        st.session_state.latitude,
        st.session_state.longitude,
        DEFAULT_ZOOM_LEVEL,
    )

    # Add markers and circles
    map_obj = add_center_marker(
        map_obj,
        st.session_state.latitude,
        st.session_state.longitude,
        st.session_state.location_name,
    )

    # Get selected radius from session state
    selected_radius = st.session_state.get("selected_radius", DEFAULT_RADIUS)
    map_obj = add_radius_circle(
        map_obj, st.session_state.latitude, st.session_state.longitude, selected_radius
    )

    # Get optimal locations and add markers
    optimal_locs = get_optimal_locations_for_radius(selected_radius)
    map_obj = add_optimal_location_markers(map_obj, optimal_locs)

    # Render map
    render_map(map_obj, height=600)

    # Display optimal locations panel
    optimal_locs = get_optimal_locations_for_radius(st.session_state.selected_radius)
    render_optimal_locations_panel(optimal_locs, st.session_state.selected_radius)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888;'>
        🌟 AI Skyline Visibility Map | Made with Streamlit & Folium 🌟
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
