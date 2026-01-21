"""
Map display components for the main application.
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
from typing import Dict, List, Any


def render_map(map_obj: folium.Map, height: int = 600) -> Dict[str, Any]:
    """
    Render a folium map using streamlit-folium.

    Args:
        map_obj: Folium map object to render
        height: Height of map in pixels

    Returns:
        Dict: User interactions with the map (if any)
    """
    map_data = st_folium(map_obj, width=1400, height=height)
    return map_data


def render_optimal_locations_panel(locations: List[Dict[str, Any]], radius_km: int) -> None:
    """
    Render the bottom panel with optimal observation locations.

    Args:
        locations: List of optimal location dictionaries
        radius_km: Search radius in kilometers
    """
    st.markdown("---")
    st.markdown(f"## 🎯 Optimal Coordinates to Visit (within {radius_km} km)")

    # Radius selector
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**Radius:**")

    # Display locations
    if locations:
        for idx, loc in enumerate(locations, 1):
            with st.expander(
                f"📍 {idx}. {loc.get('name', 'Unknown')} - "
                f"{loc.get('distance_km', 0):.1f} km away",
                expanded=(idx == 1),  # Expand first item by default
            ):
                col1, col2, col3, col4 = st.columns(4)

                pollution_value = loc.get(
                    "light_pollution_index", loc.get("bortle_score", 0)
                )

                with col1:
                    st.metric(
                        "📏 Distance",
                        f"{loc.get('distance_km', 0):.1f} km",
                    )

                with col2:
                    st.metric(
                        "💡 Light Pollution",
                        f"{pollution_value:.2f}",
                        delta="Lower is darker",
                    )

                with col3:
                    st.metric(
                        "☁️ Cloudiness",
                        f"{loc.get('cloudiness_percent', 0)}%",
                    )

                with col4:
                    st.metric(
                        "🌕 Moon Brightness",
                        f"{loc.get('moon_brightness', 0)}%",
                    )

                st.markdown(f"**Conditions:** {loc.get('conditions', 'Unknown')}")
                st.markdown(
                    f"**Coordinates:** {loc.get('latitude', 0):.4f}, "
                    f"{loc.get('longitude', 0):.4f}"
                )

                if st.button(
                    "📍 View on Map",
                    key=f"view_location_{idx}",
                    use_container_width=True,
                ):
                    st.info(f"Centered map on {loc.get('name', 'Unknown')}")

    else:
        st.info("No optimal locations found for the selected radius.")
