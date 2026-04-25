"""Central analysis module for statistical calculations and data merging."""

import re
import pandas as pd
from scipy import stats

def aggregate_daily(observations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sightings to daily counts per species.
    
    Handles observation_count = 'X' by treating it as 1.
    
    Args:
        observations_df: DataFrame with observation_date and observation_count.
        
    Returns:
        pd.DataFrame with columns [observation_date, sighting_count].
    """
    df = observations_df.copy()
    
    # 'X' means species was present but uncounted; treat as 1.
    # Regex matches only pure integer strings; anything else (including 'X') maps to 1.
    df["sighting_count"] = df["observation_count"].apply(
        lambda v: int(v) if re.fullmatch(r"\d+", str(v).strip()) else 1
    )
    
    # Aggregate by date
    daily = df.groupby("observation_date")["sighting_count"].sum().reset_index()
    return daily

def aggregate_weather_daily(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates hourly weather data to daily metrics.
    
    Metrics:
        - temperature_2m: mean
        - precipitation: sum
        - wind_speed_10m: max
        
    Args:
        weather_df: DataFrame with 'date' and weather columns.
        
    Returns:
        pd.DataFrame: Daily weather metrics with 'date' (as string YYYY-MM-DD).
    """
    df = weather_df.copy()
    df["observation_date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    
    daily = df.groupby("observation_date").agg({
        "temperature_2m": "mean",
        "precipitation": "sum",
        "wind_speed_10m": "max"
    }).reset_index()
    
    return daily

def merge_sightings_weather(observations_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align sighting timestamps to the nearest hourly weather record.
    
    Args:
        observations_df: DataFrame with observation_date, time_observations_started.
        weather_df: DataFrame with date (UTC) and weather parameters.
        
    Returns:
        pd.DataFrame: Joined DataFrame with both sighting and weather columns.
    """
    obs = observations_df.copy()
    
    # Create datetime from date and time
    # Combine YYYY-MM-DD and HH:MM:SS
    obs["datetime"] = pd.to_datetime(
        obs["observation_date"] + " " + obs["time_observations_started"].fillna("12:00:00")
    )
    
    # Round sightings to nearest hour to match weather data
    obs["datetime_hourly"] = obs["datetime"].dt.round("h")
    
    # Ensure weather_df dates are UTC-naive or match obs
    w = weather_df.copy()
    w["datetime_hourly"] = pd.to_datetime(w["date"]).dt.tz_localize(None)
    
    # Merge
    merged = pd.merge(obs, w, on="datetime_hourly", how="inner")
    
    return merged

def pearson_correlation(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    """
    Computes Pearson correlation coefficient and p-value.
    
    Args:
        x: Data series 1.
        y: Data series 2.
        
    Returns:
        tuple: (correlation_coefficient, p_value).
    """
    # Drop rows with NaNs in either series
    valid_idx = ~(x.isna() | y.isna())
    if valid_idx.sum() < 2:
        return 0.0, 1.0
        
    res = stats.pearsonr(x[valid_idx], y[valid_idx])
    return float(res.statistic), float(res.pvalue)

def ttest_regions(region_a: pd.Series, region_b: pd.Series) -> tuple[float, float]:
    """
    Computes independent t-test between two regions.
    
    Args:
        region_a: Data series for region A.
        region_b: Data series for region B.
        
    Returns:
        tuple: (t_statistic, p_value).
    """
    # Drop NaNs
    a = region_a.dropna()
    b = region_b.dropna()
    
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
        
    res = stats.ttest_ind(a, b)
    return float(res.statistic), float(res.pvalue)
