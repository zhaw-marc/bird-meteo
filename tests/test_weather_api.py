"""Unit tests for the Open-Meteo weather API client.

AUTHOR: Marc Vogelmann
"""

import pandas as pd
from src.weather_api import get_historical_weather, get_weather_description


def test_get_weather_description():
    """Verify that WMO codes are correctly mapped to descriptions."""
    assert get_weather_description(0) == "Clear sky"
    assert get_weather_description(95) == "Thunderstorm: Slight or moderate"
    assert get_weather_description(999) == "Unknown code (999)"


def test_get_historical_weather():
    """Verify that historical weather data is fetched and formatted correctly."""
    # Test for Zurich coordinates, a few days in Jan 2024
    lat, lon = 47.3769, 8.5417
    start = "2024-01-01"
    end = "2024-01-02"

    df = get_historical_weather(lat, lon, start, end)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    # Expected columns
    expected_cols = {
        "date",
        "temperature_2m",
        "precipitation",
        "wind_speed_10m",
        "weather_code",
        "weather_description",
    }
    assert expected_cols.issubset(df.columns)

    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_float_dtype(df["temperature_2m"])
    assert pd.api.types.is_integer_dtype(df["weather_code"])

    # Check row count (48 hours for 2 full days)
    assert len(df) == 48
