"""Tests for the analysis module src/analysis.py."""

import pandas as pd
import pytest
from src.analysis import (
    aggregate_daily, 
    aggregate_weather_daily, 
    merge_sightings_weather, 
    pearson_correlation, 
    ttest_regions
)

def test_aggregate_daily():
    data = {
        "observation_date": ["2023-01-01", "2023-01-01", "2023-01-02"],
        "observation_count": ["5", "X", "10"]
    }
    df = pd.DataFrame(data)
    result = aggregate_daily(df)
    
    assert len(result) == 2
    assert result.loc[result["observation_date"] == "2023-01-01", "sighting_count"].iloc[0] == 6.0
    assert result.loc[result["observation_date"] == "2023-01-02", "sighting_count"].iloc[0] == 10.0

def test_aggregate_weather_daily():
    weather_data = {
        "date": pd.to_datetime([
            "2023-01-01 00:00:00", "2023-01-01 12:00:00", 
            "2023-01-02 00:00:00", "2023-01-02 12:00:00"
        ]),
        "temperature_2m": [0.0, 10.0, 5.0, 15.0],
        "precipitation": [1.0, 1.0, 0.0, 0.0],
        "wind_speed_10m": [10.0, 20.0, 5.0, 5.0]
    }
    df = pd.DataFrame(weather_data)
    result = aggregate_weather_daily(df)
    
    assert len(result) == 2
    # 2023-01-01: mean temp 5.0, sum prec 2.0, max wind 20.0
    row1 = result[result["observation_date"] == "2023-01-01"].iloc[0]
    assert row1["temperature_2m"] == 5.0
    assert row1["precipitation"] == 2.0
    assert row1["wind_speed_10m"] == 20.0

def test_merge_sightings_weather():
    obs_data = {
        "observation_date": ["2023-01-01", "2023-01-01"],
        "time_observations_started": ["08:15:00", "12:50:00"]
    }
    obs_df = pd.DataFrame(obs_data)
    
    weather_data = {
        "date": pd.to_datetime(["2023-01-01 08:00:00", "2023-01-01 13:00:00"]),
        "temperature_2m": [5.0, 10.0]
    }
    weather_df = pd.DataFrame(weather_data)
    
    merged = merge_sightings_weather(obs_df, weather_df)
    
    assert len(merged) == 2
    assert "temperature_2m" in merged.columns
    # 08:15 should round to 08:00
    assert merged.loc[merged["time_observations_started"] == "08:15:00", "temperature_2m"].iloc[0] == 5.0
    # 12:50 should round to 13:00
    assert merged.loc[merged["time_observations_started"] == "12:50:00", "temperature_2m"].iloc[0] == 10.0

def test_pearson_correlation():
    x = pd.Series([1, 2, 3, 4, 5])
    y = pd.Series([2, 4, 6, 8, 10])
    corr, p = pearson_correlation(x, y)
    assert corr == pytest.approx(1.0)
    assert p < 0.05

def test_ttest_regions():
    region_a = pd.Series([10, 12, 11, 13, 12])
    region_b = pd.Series([20, 22, 21, 23, 22])
    t, p = ttest_regions(region_a, region_b)
    assert t < 0  # A is smaller than B
    assert p < 0.05
