# SQLite Database – `data/ebird.db`

Erstellt durch `scripts/build_database.py` aus dem eBird Basic Dataset (Schweiz,
Release Feb-2026). Die Datenbank enthält zwei Tabellen.

---

## Tabelle `observations`

Eine Zeile pro Vogelsichtung.

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `global_unique_identifier` | TEXT (PK) | Eindeutige eBird-ID der Beobachtung |
| `common_name` | TEXT NOT NULL | Englischer Artname |
| `scientific_name` | TEXT NOT NULL | Wissenschaftlicher Artname |
| `category` | TEXT | Taxonomische Kategorie (species, subspecies, …) |
| `taxonomic_order` | INTEGER | Taxonomische Sortierung |
| `observation_count` | TEXT | Anzahl beobachteter Individuen (`X` = anwesend) |
| `locality` | TEXT | Name des Beobachtungsorts |
| `locality_id` | TEXT | eBird Locality-ID |
| `state` | TEXT | Kanton (Langname) |
| `state_code` | TEXT | Kantonscode, z.B. `CH-ZH` |
| `county` | TEXT | Bezirk / Kreis |
| `latitude` | REAL NOT NULL | Breitengrad (WGS 84) |
| `longitude` | REAL NOT NULL | Laengengrad (WGS 84) |
| `observation_date` | TEXT NOT NULL | Datum der Sichtung (`YYYY-MM-DD`) |
| `time_observations_started` | TEXT | Startzeit (`HH:MM:SS`) |
| `sampling_event_identifier` | TEXT | Verweis auf die zugehoerige Checklist |
| `protocol_code` | TEXT | Erhebungsprotokoll (z.B. `P22` = Traveling) |
| `duration_minutes` | REAL | Dauer der Begehung in Minuten |
| `effort_distance_km` | REAL | Zurueckgelegte Distanz in km |
| `number_observers` | INTEGER | Anzahl Beobachter |
| `all_species_reported` | INTEGER | 1 = komplette Checklist |
| `has_media` | INTEGER | 1 = Foto/Audio vorhanden |
| `approved` | INTEGER | 1 = von eBird validiert |
| `species_comments` | TEXT | Freitext-Kommentar zur Beobachtung |

## Tabelle `checklists`

Eine Zeile pro Sampling-Event (Checklist).

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `sampling_event_identifier` | TEXT (PK) | Eindeutige Checklist-ID |
| `locality` | TEXT | Name des Beobachtungsorts |
| `locality_id` | TEXT | eBird Locality-ID |
| `state` | TEXT | Kanton (Langname) |
| `state_code` | TEXT | Kantonscode |
| `county` | TEXT | Bezirk / Kreis |
| `latitude` | REAL NOT NULL | Breitengrad (WGS 84) |
| `longitude` | REAL NOT NULL | Laengengrad (WGS 84) |
| `observation_date` | TEXT NOT NULL | Datum (`YYYY-MM-DD`) |
| `time_observations_started` | TEXT | Startzeit (`HH:MM:SS`) |
| `observer_id` | TEXT | Anonymisierte Observer-ID |
| `protocol_code` | TEXT | Erhebungsprotokoll |
| `duration_minutes` | REAL | Dauer in Minuten |
| `effort_distance_km` | REAL | Distanz in km |
| `effort_area_ha` | REAL | Flaeche in Hektar |
| `number_observers` | INTEGER | Anzahl Beobachter |
| `all_species_reported` | INTEGER | 1 = komplette Checklist |
| `group_identifier` | TEXT | Gruppen-ID (gemeinsame Begehung) |

---

## Indexes

| Index | Tabelle | Spalte(n) |
|-------|---------|-----------|
| `idx_obs_common_name` | observations | `common_name` |
| `idx_obs_scientific_name` | observations | `scientific_name` |
| `idx_obs_date` | observations | `observation_date` |
| `idx_obs_state` | observations | `state_code` |
| `idx_obs_locality` | observations | `locality_id` |
| `idx_obs_sampling` | observations | `sampling_event_identifier` |
| `idx_chk_date` | checklists | `observation_date` |
| `idx_chk_state` | checklists | `state_code` |
| `idx_chk_locality` | checklists | `locality_id` |

---

## Datenbank neu erstellen

```bash
python scripts/download_ebird.py    # Rohdaten herunterladen (falls noetig)
python scripts/build_database.py    # TSV -> SQLite
pytest tests/test_database.py       # Build verifizieren
```

## Beispiel-Queries

```sql
-- Anzahl Sichtungen pro Art (Top 10)
SELECT common_name, COUNT(*) AS n
FROM observations
GROUP BY common_name
ORDER BY n DESC
LIMIT 10;

-- Sichtungen pro Kanton und Monat
SELECT state_code,
       SUBSTR(observation_date, 1, 7) AS month,
       COUNT(*) AS n
FROM observations
GROUP BY state_code, month
ORDER BY state_code, month;

-- Alle Sichtungen an einem bestimmten Ort mit Wetter-relevanten Feldern
SELECT common_name, observation_count, latitude, longitude,
       observation_date, time_observations_started
FROM observations
WHERE locality_id = 'L1043905'
ORDER BY observation_date;
```
