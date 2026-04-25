"""Database access module for Bird & Weather Explorer."""

import sqlite3
import pandas as pd
from src.config import DB_PATH

def get_species_list() -> list[str]:
    """Returns a sorted list of all distinct species common names."""
    query = "SELECT DISTINCT common_name FROM observations ORDER BY common_name"
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)
    return df["common_name"].tolist()

def get_cantons() -> list[str]:
    """Returns a sorted list of all distinct canton state codes."""
    query = "SELECT DISTINCT state_code FROM observations ORDER BY state_code"
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)
    return df["state_code"].tolist()

def get_observations(species: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns filtered observations for a specific species and date range.
    
    Args:
        species: Common name of the species.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        
    Returns:
        pd.DataFrame with columns: latitude, longitude, observation_date,
        time_observations_started, observation_count, locality_id, state_code.
    """
    query = """
        SELECT 
            latitude, 
            longitude, 
            observation_date, 
            time_observations_started, 
            observation_count, 
            locality_id, 
            state_code
        FROM observations
        WHERE common_name = ?
          AND observation_date BETWEEN ? AND ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(species, start_date, end_date))

def get_observations_basic(species: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns basic observation data for analysis (lat, lon, date, count).
    """
    query = """
        SELECT 
            latitude, 
            longitude, 
            observation_date, 
            observation_count
        FROM observations
        WHERE common_name = ?
          AND observation_date BETWEEN ? AND ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(species, start_date, end_date))

def get_observations_by_region(state_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns filtered observations for a specific canton and date range.
    
    Args:
        state_code: State code (e.g., 'CH-ZH').
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        
    Returns:
        pd.DataFrame with columns: latitude, longitude, observation_date,
        time_observations_started, observation_count, locality_id, state_code.
    """
    query = """
        SELECT 
            latitude, 
            longitude, 
            observation_date, 
            time_observations_started, 
            observation_count, 
            locality_id, 
            state_code
        FROM observations
        WHERE state_code = ?
          AND observation_date BETWEEN ? AND ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(state_code, start_date, end_date))

def get_observations_for_map(species: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns aggregated observations for map visualization.
    
    Aggregates by locality_id to reduce row count while maintaining density information.
    
    Returns:
        pd.DataFrame with columns: latitude, longitude, total_count.
    """
    query = """
        SELECT 
            latitude, 
            longitude, 
            SUM(CASE WHEN observation_count = 'X' THEN 1 ELSE CAST(observation_count AS INTEGER) END) as total_count
        FROM observations
        WHERE common_name = ?
          AND observation_date BETWEEN ? AND ?
        GROUP BY locality_id
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(species, start_date, end_date))

def get_daily_sightings_by_region(species: str, state_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns daily aggregated sightings for a specific species and canton.
    
    Returns:
        pd.DataFrame with columns: observation_date, sighting_count.
    """
    query = """
        SELECT 
            observation_date,
            SUM(CASE WHEN observation_count = 'X' THEN 1 ELSE CAST(observation_count AS INTEGER) END) as sighting_count
        FROM observations
        WHERE common_name = ?
          AND state_code = ?
          AND observation_date BETWEEN ? AND ?
        GROUP BY observation_date
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(species, state_code, start_date, end_date))

def get_daily_sightings_by_bbox(species: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Returns daily aggregated sightings for a specific species within a bounding box.
    """
    query = """
        SELECT 
            observation_date,
            SUM(CASE WHEN observation_count = 'X' THEN 1 ELSE CAST(observation_count AS INTEGER) END) as sighting_count
        FROM observations
        WHERE common_name = ?
          AND latitude BETWEEN ? AND ?
          AND longitude BETWEEN ? AND ?
          AND observation_date BETWEEN ? AND ?
        GROUP BY observation_date
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(species, min_lat, max_lat, min_lon, max_lon, start_date, end_date))
