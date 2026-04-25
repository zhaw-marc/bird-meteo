#!/usr/bin/env python3
"""Import the eBird Basic Dataset (TSV) into a SQLite database.

Reads the observation and sampling TSV files from data/ebird/
and writes data/ebird.db.

Only columns relevant for the weather–bird analysis are kept.

AUTHOR: Marc Vogelmann
"""

import csv
import glob
import os
import sqlite3
import sys

csv.field_size_limit(sys.maxsize)

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
DATA_DIR = os.path.join(BASE_DIR, "data")
EBIRD_DIR = os.path.join(DATA_DIR, "ebird")
DB_PATH = os.path.join(DATA_DIR, "ebird.db")

# ── Columns to keep from the observations file ──────────────────────────────
OBS_COLUMNS = [
    "GLOBAL UNIQUE IDENTIFIER",
    "COMMON NAME",
    "SCIENTIFIC NAME",
    "CATEGORY",
    "TAXONOMIC ORDER",
    "OBSERVATION COUNT",
    "LOCALITY",
    "LOCALITY ID",
    "STATE",
    "STATE CODE",
    "COUNTY",
    "LATITUDE",
    "LONGITUDE",
    "OBSERVATION DATE",
    "TIME OBSERVATIONS STARTED",
    "SAMPLING EVENT IDENTIFIER",
    "PROTOCOL CODE",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "NUMBER OBSERVERS",
    "ALL SPECIES REPORTED",
    "HAS MEDIA",
    "APPROVED",
    "SPECIES COMMENTS",
]

# ── Columns to keep from the sampling (checklist) file ───────────────────────
SAMPLING_COLUMNS = [
    "SAMPLING EVENT IDENTIFIER",
    "LOCALITY",
    "LOCALITY ID",
    "STATE",
    "STATE CODE",
    "COUNTY",
    "LATITUDE",
    "LONGITUDE",
    "OBSERVATION DATE",
    "TIME OBSERVATIONS STARTED",
    "OBSERVER ID",
    "PROTOCOL CODE",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "EFFORT AREA HA",
    "NUMBER OBSERVERS",
    "ALL SPECIES REPORTED",
    "GROUP IDENTIFIER",
]

# ── SQL helpers ──────────────────────────────────────────────────────────────

SQL_CREATE_OBSERVATIONS = """
CREATE TABLE IF NOT EXISTS observations (
    global_unique_identifier TEXT PRIMARY KEY,
    common_name              TEXT NOT NULL,
    scientific_name          TEXT NOT NULL,
    category                 TEXT,
    taxonomic_order          INTEGER,
    observation_count        TEXT,
    locality                 TEXT,
    locality_id              TEXT,
    state                    TEXT,
    state_code               TEXT,
    county                   TEXT,
    latitude                 REAL NOT NULL,
    longitude                REAL NOT NULL,
    observation_date         TEXT NOT NULL,
    time_observations_started TEXT,
    sampling_event_identifier TEXT,
    protocol_code            TEXT,
    duration_minutes         REAL,
    effort_distance_km       REAL,
    number_observers         INTEGER,
    all_species_reported     INTEGER,
    has_media                INTEGER,
    approved                 INTEGER,
    species_comments         TEXT
);
"""

SQL_CREATE_CHECKLISTS = """
CREATE TABLE IF NOT EXISTS checklists (
    sampling_event_identifier TEXT PRIMARY KEY,
    locality                  TEXT,
    locality_id               TEXT,
    state                     TEXT,
    state_code                TEXT,
    county                    TEXT,
    latitude                  REAL NOT NULL,
    longitude                 REAL NOT NULL,
    observation_date          TEXT NOT NULL,
    time_observations_started TEXT,
    observer_id               TEXT,
    protocol_code             TEXT,
    duration_minutes          REAL,
    effort_distance_km        REAL,
    effort_area_ha            REAL,
    number_observers          INTEGER,
    all_species_reported      INTEGER,
    group_identifier          TEXT
);
"""

SQL_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_obs_common_name ON observations(common_name);",
    "CREATE INDEX IF NOT EXISTS idx_obs_scientific_name ON observations(scientific_name);",
    "CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(observation_date);",
    "CREATE INDEX IF NOT EXISTS idx_obs_state ON observations(state_code);",
    "CREATE INDEX IF NOT EXISTS idx_obs_locality ON observations(locality_id);",
    "CREATE INDEX IF NOT EXISTS idx_obs_sampling ON observations(sampling_event_identifier);",
    "CREATE INDEX IF NOT EXISTS idx_chk_date ON checklists(observation_date);",
    "CREATE INDEX IF NOT EXISTS idx_chk_state ON checklists(state_code);",
    "CREATE INDEX IF NOT EXISTS idx_chk_locality ON checklists(locality_id);",
]


def _to_snake(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("/", "_")


def _cast(value: str, col_snake: str) -> object:
    """Best-effort type casting for a column value."""
    value = value.strip()
    if value == "":
        return None

    # Boolean-ish columns stored as 0/1
    if col_snake in ("all_species_reported", "has_media", "approved"):
        return 1 if value == "1" else 0

    # Numeric columns
    if col_snake in (
        "taxonomic_order",
        "number_observers",
    ):
        try:
            return int(value)
        except ValueError:
            return None

    if col_snake in (
        "duration_minutes",
        "effort_distance_km",
        "effort_area_ha",
        "latitude",
        "longitude",
    ):
        try:
            return float(value)
        except ValueError:
            return None

    return value


def _import_tsv(
    conn: sqlite3.Connection,
    path: str,
    table: str,
    keep_columns: list[str],
    batch_size: int = 50_000,
) -> int:
    """Read a TSV and insert selected columns into *table*. Returns row count."""
    snake_cols = [_to_snake(c) for c in keep_columns]
    placeholders = ", ".join("?" for _ in snake_cols)
    col_list = ", ".join(snake_cols)
    insert_sql = f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})"

    total = 0
    batch: list[tuple] = []

    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            values = tuple(_cast(row[c], sc) for c, sc in zip(keep_columns, snake_cols))
            batch.append(values)
            if len(batch) >= batch_size:
                conn.executemany(insert_sql, batch)
                conn.commit()
                total += len(batch)
                print(f"\r  {table}: {total:,} rows", end="", flush=True)
                batch.clear()

    if batch:
        conn.executemany(insert_sql, batch)
        conn.commit()
        total += len(batch)

    print(f"\r  {table}: {total:,} rows (done)")
    return total


def main() -> None:
    # Dynamically find the observation and sampling files recursively
    # (Handling cases where the ZIP contains subdirectories)
    all_txt_files = glob.glob(os.path.join(EBIRD_DIR, "**", "*.txt"), recursive=True)
    
    sampling_files = [f for f in all_txt_files if f.endswith("_sampling.txt")]
    obs_files = [
        f for f in all_txt_files 
        if os.path.basename(f).startswith("ebd_") 
        and f.endswith(".txt")
        and not f.endswith("_sampling.txt")
    ]

    if not obs_files:
        sys.exit(
            f"Observations file not found in {EBIRD_DIR}\n"
            "Run scripts/download_ebird.py first."
        )
    if not sampling_files:
        sys.exit(
            f"Sampling file not found in {EBIRD_DIR}\n"
            "Run scripts/download_ebird.py first."
        )

    obs_path = obs_files[0]
    sampling_path = sampling_files[0]

    # Remove old DB so we get a clean build
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    print("Creating tables ...")
    conn.executescript(SQL_CREATE_OBSERVATIONS)
    conn.executescript(SQL_CREATE_CHECKLISTS)

    print(f"Importing observations from {os.path.basename(obs_path)} ...")
    _import_tsv(conn, obs_path, "observations", OBS_COLUMNS)

    print(f"Importing checklists from {os.path.basename(sampling_path)} ...")
    _import_tsv(conn, sampling_path, "checklists", SAMPLING_COLUMNS)

    print("Creating indexes ...")
    for idx_sql in SQL_CREATE_INDEXES:
        conn.execute(idx_sql)
    conn.commit()

    # Summary
    obs_count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    chk_count = conn.execute("SELECT COUNT(*) FROM checklists").fetchone()[0]
    species = conn.execute("SELECT COUNT(DISTINCT common_name) FROM observations").fetchone()[0]
    print(f"\nDatabase ready at {os.path.abspath(DB_PATH)}")
    print(f"  Observations : {obs_count:,}")
    print(f"  Checklists   : {chk_count:,}")
    print(f"  Species      : {species:,}")

    conn.close()


if __name__ == "__main__":
    main()
