import streamlit as st
import sys
import os

# Add project root to sys.path to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from components.sidebar import render_sidebar
from src.db import get_observations_for_map

st.set_page_config(page_title="Map - Bird & Weather Explorer", page_icon="📍", layout="wide")

# Render sidebar and get filters
filters = render_sidebar()

st.title("📍 Bird Sighting Map")
st.markdown(f"Visualizing sightings of **{filters['species']}** from **{filters['start_date']}** to **{filters['end_date']}**")

# Fetch data
with st.spinner("Fetching observation data..."):
    df = get_observations_for_map(
        filters["species"], 
        filters["start_date"].strftime("%Y-%m-%d"), 
        filters["end_date"].strftime("%Y-%m-%d")
    )

if df.empty:
    st.warning("No observations found for the selected filters.")
else:
    # Summary Metrics
    total_sightings = int(df["total_count"].sum())
    unique_locations = len(df)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Individuals Sighted", f"{total_sightings:,}")
    col2.metric("Unique Locations", f"{unique_locations:,}")

    # Create map
    # Switzerland center: 46.8, 8.2
    m = folium.Map(location=[46.8, 8.2], zoom_start=8, tiles="CartoDB positron")

    # Prepare data for HeatMap: list of [lat, lon, weight]
    heat_data = df[["latitude", "longitude", "total_count"]].values.tolist()

    # Add HeatMap layer
    HeatMap(heat_data, radius=15, blur=10).add_to(m)

    # Render map
    st_folium(m, width=1200, height=600, returned_objects=[])

    st.caption("Intensity reflects density of sightings. Data aggregated by locality.")
