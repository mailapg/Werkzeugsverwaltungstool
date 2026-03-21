# Werkzeugverwaltung – Frontend

React-Frontend für das Werkzeugverwaltungstool. Gebaut mit Vite, TypeScript, Tailwind CSS v4 und shadcn/ui.

---

## Tech Stack

| Technologie | Version | Zweck |
|---|---|---|
| React | 19 | UI Framework |
| TypeScript | 5.9 | Typsicherheit |
| Vite | 7 | Build Tool & Dev Server |
| Tailwind CSS | v4 | Styling |
| shadcn/ui | 3.8 | UI Komponenten |
| React Router | v7 | Client-seitiges Routing |
| Axios | 1.x | HTTP Client |
| Recharts | 3.x | Diagramme / Charts |
| Sonner | 2.x | Toast Notifications |
| lucide-react | – | Icons |
| jwt-decode | 4.x | JWT Token Parsing |

---

## Voraussetzungen

- **Node.js** >= 18
- **npm** >= 9
- Das [Backend](../backend/README.md) muss laufen (Standard: `http://localhost:8000`)

---

## Setup

```bash
# 1. In das Frontend-Verzeichnis wechseln
cd frontend

# 2. Abhängigkeiten installieren
npm install

# 3. Umgebungsvariable setzen (optional, Standard ist http://localhost:8000)
cp .env.example .env
# VITE_API_URL=http://localhost:8000
```

---

## Entwicklung starten

```bash
npm run dev
```

Die App ist dann unter **http://localhost:5173** erreichbar.

---

## Verfügbare Scripts

| Befehl | Beschreibung |
|---|---|
| `npm run dev` | Dev Server starten (HMR) |
| `npm run build` | Produktions-Build erstellen |
| `npm run preview` | Produktions-Build lokal vorschauen |
| `npm run lint` | ESLint ausführen |

---

## Umgebungsvariablen

Datei: `.env` im `frontend/`-Verzeichnis

```env
VITE_API_URL=http://localhost:8000
```

> Wird für API-Anfragen und das Laden von Tool-Bildern (`/static/tool_images/`) verwendet.

---

## Projektstruktur

```
frontend/
├── public/                  # Statische Assets
├── src/
│   ├── api/
│   │   ├── client.ts        # Axios-Instanz mit Auth-Header
│   │   └── services.ts      # API-Funktionen pro Ressource
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx    # Haupt-Layout (Sidebar + Content)
│   │   │   └── Sidebar.tsx      # Navigation, rollenbasiert
│   │   ├── ui/              # shadcn/ui Komponenten
│   │   └── ProtectedRoute.tsx   # Auth Guard
│   ├── contexts/
│   │   └── AuthContext.tsx  # JWT Auth State & Login/Logout
│   ├── lib/
│   │   ├── labels.ts        # Deutsche Übersetzungen für Enum-Werte
│   │   └── utils.ts         # cn() Hilfsfunktion
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ToolsPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── ToolItemDetailPage.tsx
│   │   ├── LoanRequestsPage.tsx
│   │   ├── LoansPage.tsx
│   │   ├── IssuesPage.tsx
│   │   ├── DepartmentsPage.tsx
│   │   ├── UsersPage.tsx
│   │   └── RolesPage.tsx
│   ├── types/
│   │   └── index.ts         # TypeScript Interfaces (API-Typen)
│   ├── App.tsx              # Routing-Konfiguration
│   └── main.tsx             # Einstiegspunkt
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Rollen & Berechtigungen

| Seite | ADMIN | DEPARTMENT_MANAGER | EMPLOYEE |
|---|:---:|:---:|:---:|
| Dashboard | ✓ | ✓ | ✓ |
| Werkzeuge | ✓ | ✓ | ✓ |
| Inventar | ✓ | ✓ | ✓ |
| Ausleiheanfragen | ✓ | ✓ | ✓ |
| Ausleihen | ✓ | ✓ | ✓ |
| Meldungen | ✓ | – | – |
| Abteilungen | ✓ | ✓ | – |
| Nutzer | ✓ | – | – |
| Rollen | ✓ | – | – |

> **Abteilungsleiter** können Ausleiheanfragen ohne manuelle Genehmigung direkt erstellen (automatische Freigabe).

---

## Authentifizierung

- Login über `POST /auth/login` → JWT Token
- Token wird im `localStorage` gespeichert (`access_token`)
- Axios-Client fügt den Token automatisch als `Authorization: Bearer ...` Header hinzu
- Abgelaufene oder ungültige Tokens leiten auf `/login` weiter

---

## Produktions-Build

```bash
npm run build
```

Der Build landet im `dist/`-Verzeichnis und kann von einem beliebigen Static File Server ausgeliefert werden (z. B. nginx, Caddy oder `npm run preview` für lokale Tests).
