import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from components.sidebar import render_sidebar
from src.db import get_observations_for_map
from src.config import CH_CENTER_LAT, CH_CENTER_LON, MAP_ZOOM_START, HEATMAP_RADIUS, HEATMAP_BLUR

st.set_page_config(page_title="Map - Bird & Weather Explorer", layout="wide")

filters = render_sidebar()

st.title("Bird Sighting Map")
st.markdown(f"Visualizing sightings of **{filters['species']}** from **{filters['start_date']}** to **{filters['end_date']}**")

with st.spinner("Fetching observation data..."):
    df = get_observations_for_map(
        filters["species"],
        filters["start_date"].strftime("%Y-%m-%d"),
        filters["end_date"].strftime("%Y-%m-%d")
    )

if df.empty:
    st.warning("No observations found for the selected filters.")
else:
    total_sightings = int(df["total_count"].sum())
    unique_locations = len(df)

    col1, col2 = st.columns(2)
    col1.metric("Total Individuals Sighted", f"{total_sightings:,}")
    col2.metric("Unique Locations", f"{unique_locations:,}")

    m = folium.Map(location=[CH_CENTER_LAT, CH_CENTER_LON], zoom_start=MAP_ZOOM_START, tiles="CartoDB positron")
    heat_data = df[["latitude", "longitude", "total_count"]].values.tolist()
    HeatMap(heat_data, radius=HEATMAP_RADIUS, blur=HEATMAP_BLUR).add_to(m)
    st_folium(m, width=1200, height=600, returned_objects=[])

    st.caption("Intensity reflects density of sightings. Data aggregated by locality.")
