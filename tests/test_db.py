"""Tests for the database access module src/db.py."""

import pytest
import pandas as pd
from src.db import get_species_list, get_cantons, get_observations, get_observations_by_region

def test_get_species_list():
    species = get_species_list()
    assert isinstance(species, list)
    assert len(species) > 0
    assert "Eurasian Blackbird" in species
    # Check if sorted
    assert species == sorted(species)

def test_get_cantons():
    cantons = get_cantons()
    assert isinstance(cantons, list)
    assert len(cantons) > 0
    assert "CH-ZH" in cantons
    # Check if sorted
    assert cantons == sorted(cantons)

def test_get_observations():
    df = get_observations("Eurasian Blackbird", "2023-01-01", "2023-01-31")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = [
        "latitude", 
        "longitude", 
        "observation_date", 
        "time_observations_started", 
        "observation_count", 
        "locality_id", 
        "state_code"
    ]
    for col in expected_columns:
        assert col in df.columns
    
    # Check filtering
    assert (df["observation_date"] >= "2023-01-01").all()
    assert (df["observation_date"] <= "2023-01-31").all()

def test_get_observations_by_region():
    df = get_observations_by_region("CH-ZH", "2023-01-01", "2023-01-31")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = [
        "latitude", 
        "longitude", 
        "observation_date", 
        "time_observations_started", 
        "observation_count", 
        "locality_id", 
        "state_code"
    ]
    for col in expected_columns:
        assert col in df.columns
        
    # Check filtering
    assert (df["state_code"] == "CH-ZH").all()
    assert (df["observation_date"] >= "2023-01-01").all()
    assert (df["observation_date"] <= "2023-01-31").all()
