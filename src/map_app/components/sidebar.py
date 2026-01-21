"""
Sidebar UI components for displaying location metrics.
"""

import streamlit as st
from typing import Dict, Any


def render_sidebar_metrics(metrics: Dict[str, Any]) -> None:
    """
    Render location metrics in the sidebar.

    Args:
        metrics: Dictionary containing Bortle score, cloudiness, moon brightness
    """
    with st.sidebar:
        st.markdown("## 📊 Current Location Metrics")
        st.divider()

        # Light pollution score derived from map colors
        light_pollution = metrics.get("light_pollution_index", metrics.get("bortle_score", 5))
        st.metric(
            label="💡 Light Pollution",
            value=f"{light_pollution:.2f}",
            delta="Lower is darker",
        )
        st.caption(
            "Scale from light pollution map (0 = darkest, higher = brighter skies)"
        )

        st.divider()

        # Cloudiness
        cloudiness = metrics.get("cloudiness_percent", 0)
        st.metric(
            label="☁️ Cloudiness",
            value=f"{cloudiness}%",
            delta="Lower is better for observation",
        )
        st.caption("Cloud coverage at current location")

        st.divider()

        # Moon Brightness
        moon_brightness = metrics.get("moon_brightness", 0)
        st.metric(
            label="🌕 Moon Brightness",
            value=f"{moon_brightness}%",
            delta="Lower is better for observation",
        )
        st.caption("Moon illumination and brightness level")

        st.divider()

        # Location Info
        st.markdown("### 📍 Location Info")
        st.info(
            f"""
            **Latitude:** {metrics.get('latitude', 0):.4f}  
            **Longitude:** {metrics.get('longitude', 0):.4f}  
            **Location:** {metrics.get('location_name', 'Unknown')}
            """
        )
