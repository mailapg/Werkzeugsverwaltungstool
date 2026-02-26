# Wochenbericht – KW 9 / 2026 (23.02.–27.02.2026)

> **Projekt:** Werkzeugverwaltungstool
> **Ausbildung:** Fachinformatikerin für Anwendungsentwicklung
> **Schwerpunkt der Woche:** Authentifizierung, vollständige CRUD-Schicht, alle API-Endpunkte & Testsuite
> **Autorin:** Maila Anna Pignari

<br/>

## Was ich diese Woche gemacht habe
- **Authentifizierung implementiert:** JWT-Login, `get_current_user`- und `require_role`-Dependency; sicherer Logout über server-seitigen Token-Blacklist (`BlacklistedToken`-Tabelle, wird bei jedem Request geprüft).
- **CRUD-Schicht** für alle Entitäten umgesetzt (Rollen, Abteilungen, Nutzer, Werkzeuge, Inventarstücke, Issues, Ausleiheanfragen, Ausleihen) inkl. Verfügbarkeitsprüfung, Auto-AVAILABLE-Status und automatischer Loan-Erstellung bei Genehmigung.
- **Alle API-Endpunkte** eingebunden (`/api/v1/...`): Standard-CRUD + Sonderendpunkte (Retire, Verlaufsanzeige, QR-Code-Generierung, überfällige Ausleihen, Abteilungsfilter für DEPARTMENT_MANAGER).
- **Testsuite** mit `pytest` + In-Memory-SQLite aufgesetzt: 12 Testdateien, alle CRUD-Operationen und Fehlerfälle abgedeckt.
- **Dokumentation** aktualisiert: Datenbankentwurf um neue Felder/Tabellen ergänzt, `UserStoriesV2.xlsx` erstellt, `requirements.txt` mit Versionen und Kommentaren versehen.
- **Demo-Seed-Skript** (`seed_demo.py`) erstellt: befüllt die Datenbank mit realistischen Testdaten – deterministisch via `random.Random(42)`, löscht vorher alle bestehenden Daten.
- **Initial-Manager-Konfiguration** (`config.py`) erweitert: Manager-Zugangsdaten (E-Mail, Passwort, Name) über Umgebungsvariablen konfigurierbar; `seed_initial.py` entsprechend angepasst.
- **Tool-Backend verfeinert:** Korrekturen und Anpassungen an Modell (`tool.py`), CRUD-Schicht (`crud/tool.py`), Schemas (`schemas/tool.py`) und API-Routen (`routes/tools.py`) sowie zugehörige Tests und Fixtures aktualisiert.
- **`backend/static/`-Verzeichnis** angelegt (für statische Dateien, z. B. generierte QR-Codes).

<br/>

## 🔭 Ausblick auf nächste Woche (KW 10)
- **Frontend-Start** mit React + Tailwind CSS + shadcn/ui:
  - Projektsetup (Vite, Routing, Auth-Kontext)
  - Login-Seite und Auth-Flow (Token speichern, geschützte Routen)
  - Erste Übersichtsseite (z. B. Werkzeug-Liste)

