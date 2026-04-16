# Contributing Guide

Diese Regeln sind für unser Team verbindlich. Wenn etwas nicht passt, sprechen
wir drüber und passen sie gemeinsam an – aber niemand ändert einseitig den
Prozess.

---

## Kommunikation

- **Wöchentliches Sync** TBD, 30 Min. Agenda: Status, Blocker,
  nächste Schritte.
- **Asynchrone Updates** bei Blockern oder wichtigen Entscheidungen direkt im
  Team-Chat, nicht erst beim nächsten Sync.
- **Entscheidungen dokumentieren**: Wichtige Architektur- oder Scope-
  Entscheidungen kommen in `docs/decisions.md` mit Datum und Begründung.
- **Keine stillen Blocker**: Wer länger als einen Tag feststeckt, fragt im
  Team-Chat um Hilfe.

---

## Git-Workflow

### Branches

- `main` ist immer lauffähig. **Niemand pusht direkt auf `main`.**
- Pro Issue ein Feature-Branch:
  `feature/<issue-nummer>-<kurzbeschreibung>`
  Beispiel: `feature/7-data-cleaning`
- Bugfix-Branches: `fix/<issue-nummer>-<kurzbeschreibung>`

### Commits

- Format: `<typ>: <was wurde gemacht>`
- Typen: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Beispiele:
  - `feat: add regex-based observation count parser`
  - `fix: handle missing coordinates in weather API call`
  - `docs: update README with setup instructions`
- Kurz, prägnant, auf Deutsch oder Englisch – aber innerhalb eines PR
  konsistent.

### Pull Requests

- Titel referenziert die Issue-Nummer (`Closes #7`).
- Beschreibung erklärt **was** geändert wurde und **warum**.
- Mindestens eine Review-Zustimmung, bevor gemergt wird.
- Kein Merge bei fehlgeschlagenen Tests.
- PRs sollten überschaubar bleiben – lieber zwei kleine als einen riesigen.

---

## Code-Konventionen

### Python-Stil

- **PEP 8** als Basis.
- **`black`** zum Formatieren (optional, aber empfohlen):
  ```bash
  pip install black
  black src/ app/
  ```
- **Sinnvolle Namen**: `sightings_per_day` statt `spd`.

### Docstrings

- Für alle öffentlichen Funktionen – kurz, auf Englisch.
- Format: Google-Style oder NumPy-Style, konsistent innerhalb eines Moduls.

```python
def pearson_correlation(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    """Compute Pearson correlation between two numeric series.

    Args:
        x: First numeric series.
        y: Second numeric series.

    Returns:
        Tuple of (correlation_coefficient, p_value).
    """
```

### Struktur

- **Imports aus `src/`**, nicht Copy-Paste in Notebooks.
  Wenn eine Funktion zweimal gebraucht wird, wandert sie in ein Modul.
- **Keine Magic Numbers**: Konstanten gehören in `src/config.py`.
- **Ein Modul = eine Verantwortlichkeit**. Wenn `data_cleaning.py` anfängt,
  Wetter-API-Calls zu machen, läuft was schief.

### Security & Secrets

- **Keine Credentials im Code.** API-Keys gehören in
  `.streamlit/secrets.toml` oder `.env`. Diese Dateien sind in `.gitignore`.
- **Keine grossen Dateien** ins Repo (> 50 MB). Rohdaten und die SQLite-DB
  sind via `.gitignore` ausgeschlossen.

---

## Issues & Project Board

- Jede Aufgabe existiert als GitHub-Issue mit Label, Assignee und Milestone.
- Wer an einem Issue arbeitet, verschiebt es auf **In Progress**.
- Fertig heisst:
  - Code gemergt in `main`
  - Tests grün
  - Definition of Done aus dem Issue erfüllt
- Neue Aufgaben, die während der Arbeit auftauchen, werden als neues Issue
  angelegt – nicht einfach nebenbei miterledigt.

---

## Qualitätssicherung

### Reproduzierbarkeit

- Jeder muss die App bei sich lokal zum Laufen bringen.
- Wenn `git pull && pip install -r requirements.txt && streamlit run ...`
  nicht klappt, ist das ein Blocker, kein Komfort-Thema.
- Wenn du neue Abhängigkeiten hinzufügst: `requirements.txt` aktualisieren
  und im PR erwähnen.

### Tests

- Für **kritische Logik** (Cleaning, Statistik) schreiben wir Tests.
- Nicht alles testen, aber die Kern-Funktionen.
- Tests laufen lassen, bevor du einen PR öffnest:
  ```bash
  pytest tests/
  ```

### Peer-Review

- In Woche 5 schaut jeder einmal über den Code der anderen.
- Checkliste: Lesbarkeit, Docstrings, keine Credentials, keine toten
  Code-Stellen, Tests sinnvoll.

---

## Umgang miteinander

- **Kritik ist am Code, nicht an der Person.** "Diese Funktion könnte man
  klarer benennen" statt "du hast das schlecht benannt".
- **Fragen sind immer willkommen** – niemand weiss alles. Lieber einmal
  fragen als eine Stunde im Stillen kämpfen.
- **Wenn jemand weniger Zeit hat** (Prüfungen, Krankheit), sagt man
  rechtzeitig Bescheid und verteilt die Last um – niemand lässt das Team
  im Stich, aber niemand muss sich auch überlasten.
- **Ehrlich sein bei Unsicherheit.** "Ich weiss nicht, wie ich das lösen
  soll" ist eine völlig legitime Aussage im Sync.

---

## Definition of Done (für Issues)

Ein Issue ist fertig, wenn:

- [ ] Code ist implementiert und funktioniert lokal
- [ ] Tests (falls vorhanden) laufen durch
- [ ] Code ist in `main` gemergt
- [ ] Definition of Done aus dem Issue-Body ist erfüllt
- [ ] Wenn neue Abhängigkeiten: `requirements.txt` aktualisiert
- [ ] Wenn neue Features: README oder Doku entsprechend angepasst
- [ ] Issue wurde auf **Done** verschoben und geschlossen
