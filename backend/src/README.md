# Werkzeugverwaltungstool

Webbasierte Werkzeug- und Inventarverwaltung mit Ausleih-Workflow (FastAPI + SQLAlchemy + Alembic + SQLite).
Dieses Projekt entsteht im Rahmen der Ausbildung zur Fachinformatikerin für Anwendungsentwicklung (IHK-Projekt).

---

## Ziel & Umfang (MVP)

Ziel ist eine webbasierte Werkzeugverwaltung, die in einer Werkstatt/Abteilung nachvollziehbar dokumentiert:
- welche Inventarstücke vorhanden sind,
- wer was ausgeliehen hat und bis wann,
- welche Anfragen genehmigt/abgelehnt wurden,
- und welche Issues/Schäden an Inventarstücken aufgetreten sind.

**MVP-Fokus:**
- Rollen/Rechte (**Admin**, **Abteilungsleiter**, **Mitarbeiter**)
- Werkzeugtypen + Inventarstücke verwalten
- Ausleihanfragen erstellen + Genehmigungsprozess (pro Abteilung)
- Ausleihe/Rückgabe dokumentieren
- Issue-Historie pro Inventarstück

---

## Features (aktueller Stand)
- Datenbankmodell für:
  - Rollen, Abteilungen, Benutzer
  - Werkzeugtypen (`tools`) und Inventarstücke (`tool_items`)
  - Ausleihanfragen inkl. Status & Positionen (`loan_requests`, `loan_request_items`)
  - Ausleihen inkl. Positionen (`loans`, `loan_items`)
  - Issues/Schäden pro Inventarstück (Historie) (`tool_item_issues`, `tool_item_issue_status`)
- Migrationen mit Alembic
- Seed-Daten (Lookups + Beispiel-Abteilung + Abteilungsleiter)
- Debug-Endpoint zur Datenbankprüfung

---

## Rollen & Rechte (Kurzüberblick)
- **Admin:** Stammdaten pflegen (Werkzeugtypen, Inventarstücke), Ausgaben/Rücknahmen dokumentieren
- **Abteilungsleiter:** Anfragen aus der eigenen Abteilung genehmigen/ablehnen
- **Mitarbeiter:** Ausleihanfragen stellen, eigene Ausleihen einsehen

---

## Fachliche Regeln
- Ein **Inventarstück (`tool_item`)** kann gleichzeitig nur **eine aktive Ausleihe** haben.
- Genehmigungen erfolgen **nur durch den Abteilungsleiter der Abteilung** des Antragstellers.
- **Issues/Schäden** werden als **Historie pro Inventarstück** erfasst (mehrere Issues möglich, bis ein Item ggf. aussortiert wird).

---


## Tech-Stack
- Python 3.9+
- FastAPI
- SQLAlchemy 2.x (ORM)
- Alembic (Migrationen)
- SQLite (lokal, via `DATABASE_URL`)
- python-dotenv / pydantic-settings (Konfiguration über `.env`)

---

## Projektstruktur (relevant)

```text
Werkzeugverwaltungstool/
└── backend/
    ├── alembic/
    │   ├── versions/
    │   │   └── 0e01b7542e26_initial_schema.py
    │   ├── env.py
    │   ├── README
    │   └── script.py.mako
    ├── src/
    │   └── app/
    │       ├── core/
    │       │   └── config.py
    │       ├── db/
    │       │   ├── __init__.py
    │       │   ├── app.db
    │       │   ├── base.py
    │       │   ├── deps.py
    │       │   └── session.py
    │       ├── models/
    │       │   ├── __init__.py
    │       │   ├── department.py
    │       │   ├── loan.py
    │       │   ├── loan_item.py
    │       │   ├── loan_request.py
    │       │   ├── loan_request_item.py
    │       │   ├── loan_request_status.py
    │       │   ├── role.py
    │       │   ├── tool.py
    │       │   ├── tool_category.py
    │       │   ├── tool_condition.py
    │       │   ├── tool_item.py
    │       │   ├── tool_item_issue.py
    │       │   ├── tool_item_issue_status.py
    │       │   ├── tool_status.py
    │       │   └── user.py
    │       ├── seed/
    │       │   ├── __init__.py
    │       │   └── seed_initial.py
    │       └── main.py
    ├── .env
    ├── .env.example
    ├── alembic.ini
    ├── README.md
    └── requirements.txt
```

---

## Voraussetzungen
- macOS (oder Linux/Windows analog)
- Python 3.9 oder höher
- (Optional) `git`

---

## Setup (macOS)

### 1) Ins Backend-Verzeichnis wechseln
```bash
cd backend
```

### 2) Virtuelle Umgebung erstellen & aktivieren
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```
Falls du ohne requirements.txt arbeitest (Minimal-Setup):
```bash
pip install fastapi uvicorn sqlalchemy alembic pydantic-settings python-dotenv passlib bcrypt
```

### 4) Environment-Datei anlegen
```bash
cp .env.example .env
```

### 5) Migrationen anwenden (DB-Schema erstellen)
```bash
alembic upgrade head
```

### 6) Seed-Daten einspielen
Legt u.a. Rollen/Statuswerte an sowie eine Beispiel-Abteilung + Abteilungsleiter.
```bash
python -m src.app.seed.seed_initial
```

### 7) Backend starten
```bash
uvicorn src.app.main:app --reload
```

### 8) API testen
	•	Swagger UI: http://127.0.0.1:8000/docs
	•	Debug-Check: http://127.0.0.1:8000/debug/db-check

---

## Alembic (Hinweis)

> Im Repository sind `alembic/` und `alembic.ini` bereits vorhanden.
> Daher musst du Alembic **nicht** initialisieren.

### Nur falls du Alembic komplett neu aufsetzen würdest (nicht nötig im Normalfall)
```bash
alembic init alembic
```

## Konfiguration

### .env

Die App lädt die Konfiguration über .env.

### .env.example

Vorlage zum Kopieren (keine echten Secrets).

## Migrationen (Schema ändern)

Wenn du Models änderst (neue Tabelle/Spalte/Relation), erstelle eine neue Migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Reset (nur Entwicklung)

Wenn du komplett neu starten möchtest (DB + Migrationen zurücksetzen):

```bash
rm -f src/app/db/app.db
rm -f alembic/versions/*.py
mkdir -p src/app/db
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
python -m src.app.seed.seed_initial
````
