import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
from google import genai
from datetime import date, timedelta

from src.db import (
    get_species_list,
    get_observations_for_map,
    get_observations_basic,
    get_cantons,
    get_daily_sightings_by_region,
    get_daily_sightings_by_bbox,
)
from src.weather_api import get_weather_data
from src.analysis import aggregate_daily, aggregate_weather_daily, pearson_correlation, ttest_regions
from src.config import (
    CH_CENTER_LAT, CH_CENTER_LON, MAP_ZOOM_START, HEATMAP_RADIUS, HEATMAP_BLUR,
    MIN_DATA_POINTS, SESSION_KEY_WEATHER_IMPACT, SESSION_KEY_COMPARE_REGIONS,
    DEFAULT_CANTON_A, DEFAULT_CANTON_B, DATA_LIMIT_DATE, DEFAULT_START_DATE,
    DATA_START_DATE, GEMINI_MODEL_ID,
)
from src.prompts import FINDINGS_PROMPT_TEMPLATE

st.set_page_config(
    page_title="Bird & Weather Explorer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────────────────────
for key, val in {
    "step": 0,
    "selected_species": "Eurasian Blackbird",
    "start_date": DEFAULT_START_DATE,
    "end_date": DATA_LIMIT_DATE,
    "date_preset": "1yr",
    "last_summary": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

STEPS = ["Setup", "Map", "Weather Impact", "Compare Regions", "Findings"]

POPULAR_SPECIES = [
    "Eurasian Blackbird",
    "Common Chaffinch",
    "Great Tit",
    "Barn Swallow",
    "European Robin",
    "Common Starling",
    "House Sparrow",
    "Common Swift",
    "Mallard",
    "White Wagtail",
]

DATE_PRESETS = {
    "3m":  "3 Months",
    "6m":  "6 Months",
    "1yr": "1 Year",
    "all": "All Time",
    "custom": "Custom",
}

_CSS = """
<style>
/* ── Global resets ─────────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.main .block-container {
    padding-top: 1.5rem;
    max-width: 1100px;
    animation: pageIn 0.35s ease forwards;
}
@keyframes pageIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Stepper ───────────────────────────────────────────── */
.stepper {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
    gap: 0;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}
.step-item:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 18px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: #e2e8f0;
    z-index: 0;
}
.step-item.done:not(:last-child)::after,
.step-item.active:not(:last-child)::after { background: #1d4ed8; }
.step-circle {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700;
    border: 2px solid #e2e8f0;
    background: white;
    color: #94a3b8;
    position: relative; z-index: 1;
    transition: all 0.25s ease;
}
.step-item.done .step-circle {
    background: #1d4ed8; border-color: #1d4ed8; color: white;
}
.step-item.active .step-circle {
    background: white; border-color: #1d4ed8; color: #1d4ed8;
    box-shadow: 0 0 0 4px rgba(29,78,216,0.12);
}
.step-label {
    margin-top: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.step-item.active .step-label { color: #1d4ed8; }
.step-item.done  .step-label  { color: #374151; }

/* ── Step heading ──────────────────────────────────────── */
.step-heading {
    font-size: 1.6rem; font-weight: 800;
    color: #0f172a; margin-bottom: 0.25rem;
}
.step-sub {
    font-size: 0.92rem; color: #64748b; margin-bottom: 1.5rem;
}

/* ── Species quick-picks ───────────────────────────────── */
.species-grid {
    display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem;
}
.sp-chip {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    background: white;
    font-size: 0.82rem;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    transition: all 0.15s ease;
}
.sp-chip:hover   { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }
.sp-chip.selected { border-color: #1d4ed8; background: #1d4ed8; color: white; }

/* ── Date preset pills ─────────────────────────────────── */
.preset-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.preset-pill {
    padding: 0.28rem 0.85rem; border-radius: 14px;
    border: 1px solid #e2e8f0; background: white;
    font-size: 0.8rem; font-weight: 600; color: #374151;
    cursor: pointer; transition: all 0.15s ease;
}
.preset-pill:hover    { border-color: #1d4ed8; color: #1d4ed8; }
.preset-pill.selected { border-color: #1d4ed8; background: #1d4ed8; color: white; }

/* ── Setup card ────────────────────────────────────────── */
.setup-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1.5rem 1.75rem; margin-bottom: 1.25rem;
}
.setup-card-title {
    font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #64748b; margin-bottom: 0.9rem;
}

/* ── Metrics ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 1rem 1.25rem;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em; color: #64748b;
}
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; color: #0f172a; }

/* ── Nav buttons ───────────────────────────────────────── */
.nav-bar {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid #e2e8f0;
}

/* ── Alert styling ─────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 6px; border-left-width: 4px; border-left-style: solid;
}

/* ── Misc ──────────────────────────────────────────────── */
hr { border-color: #e2e8f0; }
details summary { font-weight: 600; }
h1 { font-weight: 700; padding-bottom: 0.4rem; border-bottom: 2px solid #e2e8f0; margin-bottom: 1.25rem; }
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_dates(preset: str) -> tuple[date, date]:
    end = DATA_LIMIT_DATE
    if preset == "3m":
        return end - timedelta(days=90), end
    if preset == "6m":
        return end - timedelta(days=180), end
    if preset == "1yr":
        return end - timedelta(days=365), end
    if preset == "all":
        return DATA_START_DATE, end
    return st.session_state.start_date, st.session_state.end_date


def _stepper():
    current = st.session_state.step
    items = ""
    for i, label in enumerate(STEPS):
        if i < current:
            cls = "done"
            icon = "✓"
        elif i == current:
            cls = "active"
            icon = str(i + 1)
        else:
            cls = ""
            icon = str(i + 1)
        items += f"""
        <div class="step-item {cls}">
          <div class="step-circle">{icon}</div>
          <div class="step-label">{label}</div>
        </div>"""
    st.markdown(f'<div class="stepper">{items}</div>', unsafe_allow_html=True)


def _nav(back: bool = True, next_label: str = "Continue →", next_disabled: bool = False):
    col_b, _, col_n = st.columns([2, 8, 2])
    with col_b:
        if back and st.session_state.step > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
    with col_n:
        is_last = st.session_state.step >= len(STEPS) - 1
        if not is_last and next_label:
            if st.button(next_label, type="primary", use_container_width=True, disabled=next_disabled):
                st.session_state.step += 1
                st.rerun()


# ── Step 0: Setup ─────────────────────────────────────────────────────────────

def step_setup():
    st.markdown('<div class="step-heading">Choose Your Bird & Time Period</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-sub">Select a species and a date range — your choice applies to every step that follows.</div>', unsafe_allow_html=True)

    species_list = get_species_list()
    if st.session_state.selected_species not in species_list:
        st.session_state.selected_species = species_list[0]

    # ── Species ──────────────────────────────────────────────────────────────
    st.markdown('<div class="setup-card"><div class="setup-card-title">Bird Species</div>', unsafe_allow_html=True)

    quick_picks = [s for s in POPULAR_SPECIES if s in species_list]
    n_cols = min(len(quick_picks), 5)
    rows = [quick_picks[i:i + n_cols] for i in range(0, len(quick_picks), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for col, sp in zip(cols, row):
            with col:
                active = sp == st.session_state.selected_species
                btn_type = "primary" if active else "secondary"
                label = f"✓ {sp}" if active else sp
                if st.button(label, key=f"sp_{sp}", use_container_width=True, type=btn_type):
                    st.session_state.selected_species = sp
                    st.rerun()

    st.markdown("**Or search all species:**")
    current_idx = species_list.index(st.session_state.selected_species) if st.session_state.selected_species in species_list else 0
    chosen = st.selectbox(
        "All species",
        options=species_list,
        index=current_idx,
        label_visibility="collapsed",
    )
    if chosen != st.session_state.selected_species:
        st.session_state.selected_species = chosen

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Date range ───────────────────────────────────────────────────────────
    st.markdown('<div class="setup-card"><div class="setup-card-title">Date Range</div>', unsafe_allow_html=True)

    preset_cols = st.columns(len(DATE_PRESETS))
    for col, (key, label) in zip(preset_cols, DATE_PRESETS.items()):
        with col:
            selected = st.session_state.date_preset == key
            btn_label = f"{'✓ ' if selected else ''}{label}"
            if st.button(btn_label, key=f"preset_{key}", use_container_width=True,
                         type="primary" if selected else "secondary"):
                st.session_state.date_preset = key
                if key != "custom":
                    st.session_state.start_date, st.session_state.end_date = _resolve_dates(key)
                st.rerun()

    if st.session_state.date_preset == "custom":
        dr = st.date_input(
            "Pick a range",
            value=(st.session_state.start_date, st.session_state.end_date),
            min_value=DATA_START_DATE,
            max_value=DATA_LIMIT_DATE,
        )
        if isinstance(dr, (tuple, list)) and len(dr) == 2:
            st.session_state.start_date, st.session_state.end_date = dr[0], dr[1]
    else:
        start, end = _resolve_dates(st.session_state.date_preset)
        st.caption(f"{start.strftime('%d %b %Y')}  →  {end.strftime('%d %b %Y')}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(f"Ready to explore  **{st.session_state.selected_species}**  "
            f"from {st.session_state.start_date.strftime('%d %b %Y')} "
            f"to {st.session_state.end_date.strftime('%d %b %Y')}")

    _nav(back=False, next_label="Start Exploring →")


# ── Step 1: Map ───────────────────────────────────────────────────────────────

def step_map():
    species = st.session_state.selected_species
    start   = st.session_state.start_date
    end     = st.session_state.end_date

    st.markdown(f'<div class="step-heading">Sighting Map</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-sub">Where was <strong>{species}</strong> spotted across Switzerland?</div>', unsafe_allow_html=True)

    with st.spinner("Fetching observation data…"):
        df = get_observations_for_map(species, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    if df.empty:
        st.warning("No observations found for the selected filters.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Total Individuals Sighted", f"{int(df['total_count'].sum()):,}")
        col2.metric("Unique Locations", f"{len(df):,}")

        m = folium.Map(location=[CH_CENTER_LAT, CH_CENTER_LON], zoom_start=MAP_ZOOM_START, tiles="CartoDB positron")
        HeatMap(df[["latitude", "longitude", "total_count"]].values.tolist(),
                radius=HEATMAP_RADIUS, blur=HEATMAP_BLUR).add_to(m)

        legend = """
        <div style="position:fixed;bottom:30px;right:30px;z-index:1000;background:white;
                    padding:12px 16px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.18);
                    font-family:sans-serif;font-size:12px;line-height:1.5;">
          <div style="font-weight:700;margin-bottom:6px;color:#0f172a;">Sighting Density</div>
          <div style="width:140px;height:10px;border-radius:5px;
               background:linear-gradient(to right,#0000ff,#00ffff,#00ff00,#ffff00,#ff0000);
               margin-bottom:4px;"></div>
          <div style="display:flex;justify-content:space-between;width:140px;color:#64748b;">
            <span>Low</span><span>High</span></div>
        </div>"""
        m.get_root().html.add_child(folium.Element(legend))
        st_folium(m, width=1100, height=580, returned_objects=[])
        st.caption("Intensity reflects density of sightings. Data aggregated by locality.")

    _nav(next_label="Analyse Weather Impact →")


# ── Step 2: Weather Impact ────────────────────────────────────────────────────

@st.cache_data
def _fetch_weather(lat, lon, start, end):
    return get_weather_data(lat, lon, start, end)


def step_weather():
    species = st.session_state.selected_species
    start   = st.session_state.start_date
    end     = st.session_state.end_date

    st.markdown('<div class="step-heading">Weather Impact Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-sub">Does the weather affect how often <strong>{species}</strong> is spotted?</div>', unsafe_allow_html=True)

    with st.spinner("Fetching sightings…"):
        obs_df = get_observations_basic(species, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    if obs_df.empty:
        st.warning("No sightings found for the selected species and date range.")
        _nav()
        return

    lat_c = obs_df["latitude"].mean()
    lon_c = obs_df["longitude"].mean()

    with st.spinner("Fetching weather data for sighting centroid…"):
        weather_hourly = _fetch_weather(lat_c, lon_c, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    daily_obs     = aggregate_daily(obs_df)
    daily_weather = aggregate_weather_daily(weather_hourly)
    merged        = pd.merge(daily_obs, daily_weather, on="observation_date", how="inner")

    weather_params = {
        "Temperature (°C)": "temperature_2m",
        "Precipitation (mm)": "precipitation",
        "Wind Speed (km/h)": "wind_speed_10m",
    }

    st.markdown("**Select weather parameter:**")
    selected_label = st.radio(
        "Weather parameter",
        options=list(weather_params.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_col = weather_params[selected_label]

    if len(merged) < MIN_DATA_POINTS:
        st.warning(f"Not enough data points ({len(merged)}) for a reliable correlation. Minimum required: {MIN_DATA_POINTS}")
    else:
        r, p = pearson_correlation(merged[selected_col], merged["sighting_count"])

        st.session_state[SESSION_KEY_WEATHER_IMPACT] = {
            "species": species,
            "weather_param": selected_label,
            "pearson_r": r,
            "p_value": p,
            "n": len(merged),
        }

        c1, c2, c3 = st.columns(3)
        c1.metric("Correlation (r)", f"{r:.2f}")
        c2.metric("p-value", f"{p:.4e}")
        c3.metric("Data Points (Days)", len(merged))

        if p < 0.05:
            st.success("Significant correlation found (p < 0.05).")
        else:
            st.info("No statistically significant correlation found (p ≥ 0.05).")

        fig = px.scatter(
            merged, x=selected_col, y="sighting_count", trendline="ols",
            labels={selected_col: selected_label, "sighting_count": "Daily Sightings"},
            title=f"{species} vs. {selected_label}",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View raw data"):
            st.dataframe(merged)

    _nav(next_label="Compare Regions →")


# ── Step 3: Compare Regions ───────────────────────────────────────────────────

def _region_panel(prefix: str, default_canton: str, species: str, start: date, end: date):
    cantons = get_cantons()
    mode = st.radio(f"Selection mode", ["Canton", "Bounding Box"], key=f"mode_{prefix}", horizontal=True)

    if mode == "Canton":
        default_idx = cantons.index(default_canton) if default_canton in cantons else 0
        sel = st.selectbox("Canton", options=cantons, index=default_idx, key=f"canton_{prefix}")
        with st.spinner(f"Loading {sel}…"):
            df = get_daily_sightings_by_region(species, sel, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        return df, sel
    else:
        c1, c2 = st.columns(2)
        min_lat = c1.number_input("Min Latitude",  value=46.5, key=f"min_lat_{prefix}")
        max_lat = c1.number_input("Max Latitude",  value=47.0, key=f"max_lat_{prefix}")
        min_lon = c2.number_input("Min Longitude", value=8.0,  key=f"min_lon_{prefix}")
        max_lon = c2.number_input("Max Longitude", value=8.5,  key=f"max_lon_{prefix}")
        if min_lat >= max_lat:
            st.error("Min Latitude must be less than Max Latitude.")
            st.stop()
        if min_lon >= max_lon:
            st.error("Min Longitude must be less than Max Longitude.")
            st.stop()
        with st.spinner("Loading bounding box…"):
            df = get_daily_sightings_by_bbox(
                species, min_lat, max_lat, min_lon, max_lon,
                start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"),
            )
        return df, f"BBox({min_lat},{min_lon})"


def step_compare():
    species = st.session_state.selected_species
    start   = st.session_state.start_date
    end     = st.session_state.end_date

    st.markdown('<div class="step-heading">Compare Regions</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-sub">Are sighting rates of <strong>{species}</strong> significantly different between two regions?</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Region A")
        df_a, label_a = _region_panel("A", DEFAULT_CANTON_A, species, start, end)
    with col_b:
        st.subheader("Region B")
        df_b, label_b = _region_panel("B", DEFAULT_CANTON_B, species, start, end)

    if df_a.empty or df_b.empty:
        st.warning("One or both regions have no data for the selected filters.")
    else:
        n_a, n_b = len(df_a), len(df_b)
        if n_a < MIN_DATA_POINTS or n_b < MIN_DATA_POINTS:
            st.warning(f"Not enough data points (A: {n_a}, B: {n_b}). Minimum required: {MIN_DATA_POINTS}")
        else:
            t_stat, p_val = ttest_regions(df_a["sighting_count"], df_b["sighting_count"])

            st.session_state[SESSION_KEY_COMPARE_REGIONS] = {
                "region_a": label_a, "region_b": label_b,
                "metric": "Daily Sighting Count",
                "t_statistic": t_stat, "p_value": p_val,
                "n_a": n_a, "n_b": n_b,
            }

            st.divider()
            st.subheader("Statistical Comparison (Independent t-test)")

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Avg Sightings ({label_a})", f"{df_a['sighting_count'].mean():.2f}")
            c2.metric(f"Avg Sightings ({label_b})", f"{df_b['sighting_count'].mean():.2f}")
            c3.metric("p-value", f"{p_val:.4f}")

            if p_val < 0.05:
                st.success("Significant difference between regions (p < 0.05).")
            else:
                st.info("No statistically significant difference found (p ≥ 0.05).")

            df_a = df_a.copy(); df_b = df_b.copy()
            df_a["Region"] = label_a; df_b["Region"] = label_b
            combined = pd.concat([df_a, df_b])

            c_left, c_right = st.columns(2)
            with c_left:
                st.plotly_chart(
                    px.box(combined, x="Region", y="sighting_count", points="all",
                           title="Daily Sighting Distribution"),
                    use_container_width=True,
                )
            with c_right:
                st.plotly_chart(
                    px.bar(
                        pd.DataFrame({"Region": [label_a, label_b],
                                      "Average Sightings": [df_a["sighting_count"].mean(), df_b["sighting_count"].mean()]}),
                        x="Region", y="Average Sightings", title="Mean Daily Sightings",
                    ),
                    use_container_width=True,
                )

    _nav(next_label="Generate Findings →")


# ── Step 4: Findings ──────────────────────────────────────────────────────────

def step_findings():
    species = st.session_state.selected_species
    start   = st.session_state.start_date
    end     = st.session_state.end_date

    st.markdown('<div class="step-heading">Key Findings</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-sub">AI-generated scientific summary based on your analysis results.</div>', unsafe_allow_html=True)

    weather_impact  = st.session_state.get(SESSION_KEY_WEATHER_IMPACT)
    compare_regions = st.session_state.get(SESSION_KEY_COMPARE_REGIONS)

    if not weather_impact and not compare_regions:
        st.info("Complete the Weather Impact and Compare Regions steps first to enable the summary.")
        _nav()
        return

    data = {
        "species": species,
        "start_date": start,
        "end_date": end,
    }

    if weather_impact:
        data.update({
            "weather_param":    weather_impact["weather_param"],
            "pearson_r":        weather_impact["pearson_r"],
            "p_value_weather":  weather_impact["p_value"],
            "n_weather":        weather_impact["n"],
        })
    else:
        data.update({"weather_param": "N/A", "pearson_r": 0.0, "p_value_weather": 1.0, "n_weather": 0})

    if compare_regions:
        data.update({
            "region_a":         compare_regions["region_a"],
            "region_b":         compare_regions["region_b"],
            "metric":           compare_regions["metric"],
            "t_statistic":      compare_regions["t_statistic"],
            "p_value_regions":  compare_regions["p_value"],
            "n_a":              compare_regions["n_a"],
            "n_b":              compare_regions["n_b"],
        })
    else:
        data.update({"region_a": "N/A", "region_b": "N/A", "metric": "N/A",
                     "t_statistic": 0.0, "p_value_regions": 1.0, "n_a": 0, "n_b": 0})

    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in secrets. Please add it to `.streamlit/secrets.toml`.")
        _nav()
        return

    def _generate():
        client = genai.Client(api_key=api_key)
        prompt = FINDINGS_PROMPT_TEMPLATE.format(**data)
        with st.spinner("Generating summary…"):
            try:
                response = client.models.generate_content(model=GEMINI_MODEL_ID, contents=prompt)
                st.session_state.last_summary = response.text
            except Exception as e:
                st.error(f"Error generating summary: {e}")

    if weather_impact:
        with st.expander("Weather Impact results used"):
            c1, c2 = st.columns(2)
            c1.metric("Pearson r", f"{weather_impact['pearson_r']:.2f}")
            c2.metric("p-value", f"{weather_impact['p_value']:.4e}")

    if compare_regions:
        with st.expander("Region comparison results used"):
            c1, c2 = st.columns(2)
            c1.metric(compare_regions["region_a"], f"{compare_regions['n_a']} days")
            c2.metric(compare_regions["region_b"], f"{compare_regions['n_b']} days")

    st.markdown("")
    if not st.session_state.last_summary:
        if st.button("Generate Summary", type="primary"):
            _generate()
            st.rerun()
    else:
        st.markdown("---")
        st.markdown(st.session_state.last_summary)
        st.markdown("---")
        if st.button("Regenerate Summary"):
            _generate()
            st.rerun()

    _nav()  # last step — no next button rendered (is_last guard in _nav)


# ── Router ────────────────────────────────────────────────────────────────────

_stepper()

step = st.session_state.step
if   step == 0: step_setup()
elif step == 1: step_map()
elif step == 2: step_weather()
elif step == 3: step_compare()
elif step == 4: step_findings()
