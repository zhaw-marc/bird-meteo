import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Bird & Weather Explorer",
    layout="wide"
)

st.title("Bird & Weather Explorer")
st.markdown("""
Welcome to the Bird & Weather Explorer.

This application analyzes the relationship between bird sightings in Switzerland and local weather conditions.
Use the sidebar to select a species and a date range, then explore the different tabs:

- **Map**: Visualize sighting hotspots across Switzerland.
- **Weather Impact**: Analyze how weather parameters correlate with bird activity.
- **Compare Regions**: Compare bird sightings between different cantons or regions.
- **Findings**: Get an AI-generated summary of the relationship between birds and weather.
""")

filters = render_sidebar()

st.info(f"Currently selected: {filters['species']} from {filters['start_date']} to {filters['end_date']}")
