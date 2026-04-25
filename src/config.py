"""Central configuration and constants for Bird & Weather Explorer."""

import os
from datetime import date

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ebird.db")

# Analysis
REGION_COMPARISON_METRIC = "sightings_per_day"
MIN_DATA_POINTS = 10

# Data availability window
DATA_START_DATE = date(2015, 1, 1)
DATA_LIMIT_DATE = date(2024, 12, 31)
DEFAULT_START_DATE = date(2023, 1, 1)

# Map defaults (Switzerland)
CH_CENTER_LAT = 46.8
CH_CENTER_LON = 8.2
MAP_ZOOM_START = 8
HEATMAP_RADIUS = 15
HEATMAP_BLUR = 10

# Default cantons for Compare Regions tab
DEFAULT_CANTON_A = "CH-ZH"
DEFAULT_CANTON_B = "CH-BE"

# AI model
GEMINI_MODEL_ID = "gemini-2.5-flash"

# session_state key written by the Weather Impact tab, read by the Findings tab.
# Value is a dict with keys:
#   species (str), canton (str), weather_param (str),
#   pearson_r (float), p_value (float), n (int)
SESSION_KEY_WEATHER_IMPACT = "weather_impact_result"

# session_state key written by the Compare Regions tab, read by the Findings tab.
# Value is a dict with keys:
#   region_a (str), region_b (str), metric (str),
#   t_statistic (float), p_value (float), n_a (int), n_b (int)
SESSION_KEY_COMPARE_REGIONS = "compare_regions_result"
