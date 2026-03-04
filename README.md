# Werkzeugverwaltungstool

Webbasierte Werkzeug- und Inventarverwaltung mit Ausleih-Workflow, Genehmigungsprozess und Schadensmeldungen. Entwickelt im Rahmen der Ausbildung zur Fachinformatikerin für Anwendungsentwicklung (IHK-Projekt).

---

## Projektübersicht

| | |
|---|---|
| **Backend** | FastAPI + SQLAlchemy + SQLite |
| **Frontend** | React + Vite + TypeScript + Tailwind CSS v4 |
| **Auth** | JWT-basiert, rollengeschützte Endpunkte |
| **Tests** | 120+ automatisierte Backend-Tests (pytest) |

---

## Rollen & Berechtigungen

| Funktion | Admin | Abteilungsleiter | Mitarbeiter |
|---|:---:|:---:|:---:|
| Werkzeuge & Inventar verwalten | ✓ | – | – |
| Ausleihanfragen stellen | ✓ | ✓ | ✓ |
| Ausleihanfragen genehmigen | ✓ | ✓ (eigene Abt.) | – |
| Eigene Anfragen direkt ausleihen | – | ✓ (auto-genehmigt) | – |
| Ausleihen & Rückgaben einsehen | ✓ (alle) | ✓ (eigene Abt.) | ✓ (eigene) |
| Schadensmeldungen | ✓ | – | – |
| Nutzer / Rollen / Abteilungen | ✓ | – | – |

---

## Voraussetzungen

- **Python** >= 3.9
- **Node.js** >= 18 + **npm** >= 9
- **git**

---

## Schnellstart

### 1. Repository klonen

```bash
git clone <repo-url>
cd Werkzeugverwaltungstool
```

---

### 2. Backend starten

```bash
cd backend

# Virtuelle Umgebung erstellen & aktivieren
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r src/requirements.txt

# Umgebungsvariablen setzen
cp .env.example .env

# Datenbankschema erstellen
alembic upgrade head

# Seed-Daten einspielen (Rollen, Statuswerte, Demo-Nutzer)
python -m src.app.seed.seed_initial

# Server starten
uvicorn src.app.main:app --reload
```

Backend läuft unter: **http://localhost:8000**
API-Dokumentation (Swagger): **http://localhost:8000/docs**

---

### 3. Frontend starten

```bash
cd frontend

# Abhängigkeiten installieren
npm install

# Umgebungsvariable setzen (optional, Standard: http://localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env

# Dev Server starten
npm run dev
```

Frontend läuft unter: **http://localhost:5173**

---

## Projektstruktur

```
Werkzeugverwaltungstool/
├── backend/
│   ├── alembic/                  # Datenbankmigrationen
│   ├── src/
│   │   └── app/
│   │       ├── api/routes/       # FastAPI Endpunkte
│   │       ├── auth/             # JWT Auth & Rollenprüfung
│   │       ├── crud/             # Datenbankoperationen
│   │       ├── db/               # Session, Abhängigkeiten, app.db
│   │       ├── models/           # SQLAlchemy Modelle
│   │       ├── schemas/          # Pydantic Schemas
│   │       ├── seed/             # Demo-Daten Skript
│   │       └── main.py           # App-Einstiegspunkt + CORS
│   ├── static/tool_images/       # Werkzeugbilder (PNG)
│   ├── tests/                    # pytest Testsuite (120+ Tests)
│   ├── .env.example
│   └── src/requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                  # Axios-Client + Service-Funktionen
│   │   ├── components/           # Layout, shadcn/ui Komponenten
│   │   ├── contexts/             # Auth-Kontext
│   │   ├── lib/                  # Hilfsfunktionen, Übersetzungen
│   │   ├── pages/                # Alle Seiten (Login, Dashboard, …)
│   │   ├── types/                # TypeScript Interfaces
│   │   └── App.tsx               # Routing
│   ├── .env.example
│   └── package.json
│
├── weeklies/                     # Wochenberichte KW7–KW12
└── README.md
```

---

## Umgebungsvariablen

### Backend (`backend/.env`)

```env
DATABASE_URL=sqlite:///./src/app/db/app.db
SECRET_KEY=dein-geheimer-schluessel
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

---

## Backend-Tests ausführen

```bash
cd backend
source .venv/bin/activate
pytest
```

---

## Produktions-Build (Frontend)

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

---

## Weitere Dokumentation

- [Backend README](backend/src/README.md) – Datenbankschema, Migrationen, Reset
- [Frontend README](frontend/README.md) – Tech Stack, Seiten, Rollenübersicht
