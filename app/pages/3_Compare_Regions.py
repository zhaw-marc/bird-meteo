import streamlit as st
import sys
import os

# Add project root to sys.path to find the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.sidebar import render_sidebar
from src.db import get_cantons, get_daily_sightings_by_region, get_daily_sightings_by_bbox
from src.analysis import ttest_regions
from src.config import MIN_DATA_POINTS, SESSION_KEY_COMPARE_REGIONS

st.set_page_config(page_title="Compare Regions - Bird & Weather Explorer", page_icon="⚖️", layout="wide")

# Render sidebar and get filters
filters = render_sidebar()

st.title("⚖️ Compare Regions")
st.markdown(f"Comparing sightings of **{filters['species']}** between two regions.")

# Get cantons for selectors
cantons = get_cantons()

def get_region_data(prefix: str, default_canton: str):
    st.subheader(f"Region {prefix}")
    mode = st.radio(f"Selection Mode ({prefix})", ["Canton", "Bounding Box"], key=f"mode_{prefix}", horizontal=True)
    
    if mode == "Canton":
        selected_canton = st.selectbox("Select Canton", options=cantons, index=cantons.index(default_canton) if default_canton in cantons else 0, key=f"canton_{prefix}")
        with st.spinner(f"Loading data for {selected_canton}..."):
            df = get_daily_sightings_by_region(
                filters["species"], 
                selected_canton, 
                filters["start_date"].strftime("%Y-%m-%d"), 
                filters["end_date"].strftime("%Y-%m-%d")
            )
        return df, selected_canton
    else:
        col1, col2 = st.columns(2)
        min_lat = col1.number_input("Min Latitude", value=46.5, key=f"min_lat_{prefix}")
        max_lat = col1.number_input("Max Latitude", value=47.0, key=f"max_lat_{prefix}")
        min_lon = col2.number_input("Min Longitude", value=8.0, key=f"min_lon_{prefix}")
        max_lon = col2.number_input("Max Longitude", value=8.5, key=f"max_lon_{prefix}")
        
        with st.spinner(f"Loading data for BBox..."):
            df = get_daily_sightings_by_bbox(
                filters["species"],
                min_lat, max_lat, min_lon, max_lon,
                filters["start_date"].strftime("%Y-%m-%d"), 
                filters["end_date"].strftime("%Y-%m-%d")
            )
        return df, f"BBox({min_lat},{min_lon})"

col_a, col_b = st.columns(2)

with col_a:
    df_a, label_a = get_region_data("A", "CH-ZH")

with col_b:
    df_b, label_b = get_region_data("B", "CH-BE")

# Analysis
if df_a.empty or df_b.empty:
    st.warning("One or both regions have no data for the selected filters.")
else:
    n_a = len(df_a)
    n_b = len(df_b)
    
    if n_a < MIN_DATA_POINTS or n_b < MIN_DATA_POINTS:
        st.warning(f"Not enough data points for a reliable t-test (Region A: {n_a}, Region B: {n_b}). Minimum required: {MIN_DATA_POINTS}")
    else:
        t_stat, p_val = ttest_regions(df_a["sighting_count"], df_b["sighting_count"])
        
        # Store for Findings
        st.session_state[SESSION_KEY_COMPARE_REGIONS] = {
            "region_a": label_a,
            "region_b": label_b,
            "metric": "Daily Sighting Count",
            "t_statistic": t_stat,
            "p_value": p_val,
            "n_a": n_a,
            "n_b": n_b
        }
        
        # Display Results
        st.divider()
        st.header("Statistical Comparison (Independent t-test)")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Avg Sightings ({label_a})", f"{df_a['sighting_count'].mean():.2f}")
        c2.metric(f"Avg Sightings ({label_b})", f"{df_b['sighting_count'].mean():.2f}")
        c3.metric("p-value", f"{p_val:.4f}")
        
        if p_val < 0.05:
            st.success(f"**Significant difference** between regions! (p < 0.05)")
        else:
            st.info("No statistically significant difference found (p >= 0.05).")
            
        # Visualizations
        st.subheader("Distributions")
        
        # Combine data for plotting
        df_a["Region"] = label_a
        df_b["Region"] = label_b
        combined_df = pd.concat([df_a, df_b])
        
        # Box plot
        fig_box = px.box(combined_df, x="Region", y="sighting_count", points="all", title="Daily Sighting Count Distribution")
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Bar chart for averages
        avg_df = pd.DataFrame({
            "Region": [label_a, label_b],
            "Average Sightings": [df_a["sighting_count"].mean(), df_b["sighting_count"].mean()]
        })
        fig_bar = px.bar(avg_df, x="Region", y="Average Sightings", title="Mean Daily Sightings Comparison")
        st.plotly_chart(fig_bar, use_container_width=True)
