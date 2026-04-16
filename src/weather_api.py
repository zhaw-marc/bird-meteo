#!/usr/bin/env python3
"""Module for fetching and processing historical weather data from Open-Meteo.

This client handles API requests, caching, retries, and maps WMO weather codes
to human-readable descriptions.

AUTHOR: Marc Vogelmann
"""

import os
from typing import Optional

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# ── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
CACHE_PATH = os.path.join(CACHE_DIR, "weather_cache")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Setup the Open-Meteo API client with cache and retry on error
# Cache expires after 1 month as historical data doesn't change
cache_session = requests_cache.CachedSession(CACHE_PATH, expire_after=2592000)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Weather code mapping based on WMO Weather interpretation codes (WW)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light intensity",
    53: "Drizzle: Moderate intensity",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light intensity",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight intensity",
    63: "Rain: Moderate intensity",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light intensity",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight intensity",
    73: "Snow fall: Moderate intensity",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# ── Functions ───────────────────────────────────────────────────────────────


def get_weather_description(code: int) -> str:
    """Map WMO weather code to a human-readable string.

    Args:
        code: The WMO weather interpretation code.

    Returns:
        A descriptive string for the weather condition.
    """
    return WEATHER_CODES.get(code, f"Unknown code ({code})")


def get_historical_weather(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Fetch historical weather data for a specific location and time range.

    Args:
        lat: Latitude (WGS84).
        lon: Longitude (WGS84).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A pandas DataFrame with hourly weather data including:
        - date (UTC)
        - temperature_2m
        - precipitation
        - wind_speed_10m
        - weather_code
        - weather_description
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m", "weather_code"],
        "timezone": "Europe/Berlin",
    }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a loop if multiple locations are queried
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["weather_code"] = hourly_weather_code.astype(int)

    df = pd.DataFrame(data=hourly_data)
    df["weather_description"] = df["weather_code"].apply(get_weather_description)

    return df
