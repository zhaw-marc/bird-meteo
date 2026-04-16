# Bird & Weather Explorer

Eine interaktive Web-App zur Analyse des Zusammenhangs zwischen Wetter und
Vogelsichtungen in der Schweiz.

> Projektarbeit im Modul Scientific Programming (FS 2026)
> Deadline: 27.05.2026

---

## Team

| Name | Rolle | GitHub |
|------|-------|--------|
| Marc Vogelmann | Infrastruktur & App-Gerüst | [@zhaw-marc] |
| Muriele Stermcnik | Daten & Statistik | [@stermmur] |
| Benjamin Werz | Externe Schnittstellen & Inhalt | [@username] |

---

## Projektbeschreibung

### Forschungsfrage

Beeinflussen Wetterbedingungen (Temperatur, Niederschlag, Wind) die Häufigkeit
und Vielfalt von Vogelsichtungen in verschiedenen Regionen der Schweiz?

### Was macht die App?

**Bird & Weather Explorer** kombiniert historische Vogelsichtungsdaten aus der
Schweiz (eBird Basic Dataset) mit aktuellen Wetterdaten (Open-Meteo API) und
ermöglicht es, statistische Zusammenhänge zwischen beidem interaktiv zu
untersuchen.

Die App besteht aus vier Tabs:

1. **Map** – Interaktive Karte mit Sichtungs-Hotspots, filterbar nach Art,
   Region und Zeitraum
2. **Weather Impact** – Korrelationsanalyse zwischen einer Vogelart und einem
   Wetterparameter, inklusive Pearson-Koeffizient und p-Wert
3. **Compare Regions** – Vergleich zweier Regionen mittels t-Test
4. **Findings** – Automatisch generierte Zusammenfassungen der wichtigsten
   Erkenntnisse (via LLM)

### Architektur

```
+-------------------+      +-------------------+
| eBird EBD Dataset |      | Open-Meteo API    |
| (statisch, CH)    |      | (on-the-fly)      |
+--------+----------+      +---------+---------+
         |                           |
         | build_database.py         | weather_api.py
         v                           v
+--------+---------+      +----------+--------+
| SQLite Database  |      | Wetter-Daten      |
| (Sichtungen)     |      | (pro Request)     |
+--------+---------+      +----------+--------+
          \                         /
           \                       /
            v                     v
         +----------------------------+
         |    Streamlit Web-App       |
         |  (Analyse & Visualisierung)|
         +----------------------------+
```

- **SQLite** speichert den gereinigten, statischen Vogeldatensatz (~2015–2024)
  und wird per SQL-Query gefiltert.
- **Open-Meteo API** liefert Wetterdaten dynamisch – nur für die Koordinaten
  und Zeiträume, die für die aktuelle Analyse relevant sind.
- **Streamlit** vereint beides in einer interaktiven Oberfläche.

---

## Setup

### Voraussetzungen

- Python 3.11 oder neuer
- Git
- ~2 GB Speicher für die eBird-Rohdaten (nicht im Repo)

### Installation

```bash
# Repo klonen
git clone https://github.com/zhaw-marc/bird-meteo.git
cd bird-meteo/

# Virtuelle Umgebung erstellen und aktivieren
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Projektstruktur

```
bird-weather-explorer/
├── app/              # Streamlit-App (Einstiegspunkt + Tabs)
├── src/              # Wiederverwendbare Module (DB, Cleaning, API, Analyse)
├── scripts/          # Einmal-Läufe (z.B. DB-Build)
├── notebooks/        # Jupyter Notebooks (Entwicklung & Exploration)
├── tests/            # Unit-Tests
├── data/             # Rohdaten & DB
├── docs/             # Architektur-Diagramm, Research Question
└── README.md
```

---

## Mitarbeit

Regeln für die Zusammenarbeit im Team (Git-Workflow, Code-Konventionen,
Kommunikation) stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Zeitplan

| Woche | Zeitraum | Fokus |
|-------|----------|-------|
| 1 | 15.–20.04. | Setup & Datenbeschaffung |
| 2 | 21.–27.04. | Datenbank & API-Anbindung |
| 3 | 28.04.–04.05. | Analyse-Logik & App-Grundgerüst |
| 4 | 05.–11.05. | App-Tabs implementieren |
| 5 | 12.–18.05. | Polishing & Präsentation |
| 6 | 19.–26.05. | Video & Abgabe |
| **Abgabe** | **27.05.** | **Moodle (vormittags)** |

Detail-Aufgaben im [GitHub Project Board](../../projects).

---

## Datenquellen

- **eBird Basic Dataset**, Cornell Lab of Ornithology.
  [ebird.org/data/download](https://ebird.org/data/download)
- **Open-Meteo Historical Weather API**.
  [open-meteo.com](https://open-meteo.com/)

## Tech-Stack

Python, Streamlit, Pandas, SQLite, SciPy, Folium, Anthropic Claude API.

