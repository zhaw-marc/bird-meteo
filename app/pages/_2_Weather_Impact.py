import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import plotly.express as px
from components.sidebar import render_sidebar
from src.db import get_observations_basic
from src.weather_api import get_weather_data
from src.analysis import aggregate_daily, aggregate_weather_daily, pearson_correlation
from src.config import MIN_DATA_POINTS, SESSION_KEY_WEATHER_IMPACT

st.set_page_config(page_title="Weather Impact - Bird & Weather Explorer", layout="wide")

filters = render_sidebar()

st.title("Weather Impact Analysis")
st.markdown(f"Analyzing how weather conditions affect sightings of **{filters['species']}**")

with st.spinner("Fetching sightings..."):
    obs_df = get_observations_basic(
        filters["species"],
        filters["start_date"].strftime("%Y-%m-%d"),
        filters["end_date"].strftime("%Y-%m-%d")
    )

if obs_df.empty:
    st.warning("No sightings found for the selected species and date range.")
    st.stop()

lat_centroid = obs_df["latitude"].mean()
lon_centroid = obs_df["longitude"].mean()


@st.cache_data
def fetch_weather(lat, lon, start, end):
    return get_weather_data(lat, lon, start, end)


with st.spinner("Fetching weather data for sighting centroid..."):
    weather_hourly_df = fetch_weather(
        lat_centroid,
        lon_centroid,
        filters["start_date"].strftime("%Y-%m-%d"),
        filters["end_date"].strftime("%Y-%m-%d")
    )

daily_obs = aggregate_daily(obs_df)
daily_weather = aggregate_weather_daily(weather_hourly_df)
merged_df = pd.merge(daily_obs, daily_weather, on="observation_date", how="inner")

weather_params = {
    "Temperature (°C)": "temperature_2m",
    "Precipitation (mm)": "precipitation",
    "Wind Speed (km/h)": "wind_speed_10m"
}
selected_label = st.selectbox("Select Weather Parameter", options=list(weather_params.keys()))
selected_col = weather_params[selected_label]

if len(merged_df) < MIN_DATA_POINTS:
    st.warning(f"Not enough data points ({len(merged_df)}) for a reliable correlation. Minimum required: {MIN_DATA_POINTS}")
else:
    r, p = pearson_correlation(merged_df[selected_col], merged_df["sighting_count"])

    st.session_state[SESSION_KEY_WEATHER_IMPACT] = {
        "species": filters["species"],
        "weather_param": selected_label,
        "pearson_r": r,
        "p_value": p,
        "n": len(merged_df)
    }

    col1, col2, col3 = st.columns(3)
    col1.metric("Correlation (r)", f"{r:.2f}")
    col2.metric("p-value", f"{p:.4e}")
    col3.metric("Data Points (Days)", len(merged_df))

    if p < 0.05:
        st.success("Significant correlation found (p < 0.05).")
    else:
        st.info("No statistically significant correlation found (p >= 0.05).")

    fig = px.scatter(
        merged_df,
        x=selected_col,
        y="sighting_count",
        labels={selected_col: selected_label, "sighting_count": "Daily Sightings"},
        title=f"{filters['species']} vs. {selected_label}",
        trendline="ols"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Data Overview")
with st.expander("View raw merged data"):
    st.write(merged_df)
