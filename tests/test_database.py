"""Tests to verify the SQLite database was built correctly."""

import os
import sqlite3

import pytest

DB_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "data", "ebird.db")

EXPECTED_OBS_COLUMNS = [
    "global_unique_identifier",
    "common_name",
    "scientific_name",
    "category",
    "taxonomic_order",
    "observation_count",
    "locality",
    "locality_id",
    "state",
    "state_code",
    "county",
    "latitude",
    "longitude",
    "observation_date",
    "time_observations_started",
    "sampling_event_identifier",
    "protocol_code",
    "duration_minutes",
    "effort_distance_km",
    "number_observers",
    "all_species_reported",
    "has_media",
    "approved",
    "species_comments",
]

EXPECTED_CHK_COLUMNS = [
    "sampling_event_identifier",
    "locality",
    "locality_id",
    "state",
    "state_code",
    "county",
    "latitude",
    "longitude",
    "observation_date",
    "time_observations_started",
    "observer_id",
    "protocol_code",
    "duration_minutes",
    "effort_distance_km",
    "effort_area_ha",
    "number_observers",
    "all_species_reported",
    "group_identifier",
]


@pytest.fixture(scope="module")
def conn():
    if not os.path.isfile(DB_PATH):
        pytest.skip("Database not found – run scripts/build_database.py first")
    connection = sqlite3.connect(DB_PATH)
    yield connection
    connection.close()


def test_tables_exist(conn):
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "observations" in tables
    assert "checklists" in tables


def test_observations_columns(conn):
    cursor = conn.execute("PRAGMA table_info(observations)")
    columns = [row[1] for row in cursor.fetchall()]
    assert columns == EXPECTED_OBS_COLUMNS


def test_checklists_columns(conn):
    cursor = conn.execute("PRAGMA table_info(checklists)")
    columns = [row[1] for row in cursor.fetchall()]
    assert columns == EXPECTED_CHK_COLUMNS


def test_observations_not_empty(conn):
    count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    assert count > 0, "observations table is empty"


def test_checklists_not_empty(conn):
    count = conn.execute("SELECT COUNT(*) FROM checklists").fetchone()[0]
    assert count > 0, "checklists table is empty"


def test_no_null_coordinates(conn):
    nulls = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE latitude IS NULL OR longitude IS NULL"
    ).fetchone()[0]
    assert nulls == 0, f"{nulls} observations with NULL coordinates"


def test_no_null_dates(conn):
    nulls = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE observation_date IS NULL"
    ).fetchone()[0]
    assert nulls == 0, f"{nulls} observations with NULL observation_date"


def test_indexes_exist(conn):
    indexes = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        ).fetchall()
    }
    expected = {
        "idx_obs_common_name",
        "idx_obs_scientific_name",
        "idx_obs_date",
        "idx_obs_state",
        "idx_obs_locality",
        "idx_obs_sampling",
        "idx_chk_date",
        "idx_chk_state",
        "idx_chk_locality",
    }
    assert expected.issubset(indexes), f"Missing indexes: {expected - indexes}"
