# Wochenbericht – KW 8 / 2026 (16.02.–20.02.2026)

> **Projekt:** Werkzeugverwaltungstool  
> **Ausbildung:** Fachinformatikerin für Anwendungsentwicklung  
> **Schwerpunkt der Woche:** Technisches Setup, Datenbank & Backend-Start (FastAPI + SQLAlchemy + Alembic)  
> **Autorin:** Maila Anna Pignari  

<br/>

## Was ich diese Woche gemacht habe
- Backend-Grundsetup erstellt (Projektstruktur, venv) und FastAPI/SQLAlchemy/Alembic als technische Basis festgelegt.
- Datenbankentwurf finalisiert und in ein konsistentes Tabellen-/Relationsmodell übersetzt (Rollen, Abteilungen, Nutzer, Werkzeuge/Inventarstücke, Ausleih-Workflow).
- 1:1 Beziehung **Department ↔ Lead-User (Abteilungsleiter)** umgesetzt und den dabei entstehenden FK-Zyklus fachlich eingeordnet.
- ORM-Models erstellt und geprüft (Foreign Keys, Relationships, Indizes/Constraints) passend zum Entwurf.
- Alembic integriert und lauffähig gemacht.
- Datenbank-Konfiguration vereinheitlicht: DB-URL zentral aus `.env` (für App, Alembic und Seed) und SQLite-Pfad bewusst innerhalb der Projektstruktur gewählt.
- Seed-Daten implementiert und erfolgreich ausgeführt (Lookup-Tabellen, Beispiel-Abteilung + Abteilungsleiter); dabei Issues wie DB-Pfad und bcrypt/passlib-Versionen behoben.
- Lehrerfeedback eingearbeitet: **Issues/Schäden als eigene Tabelle** an `tool_items` geplant/angelegt (Historie pro Inventarstück).

<br/>

## 🔭 Ausblick auf nächste Woche (KW 9)
- **Authentifizierung & Rollenprüfung** implementieren:
  - Login mit **JWT**
  - Dependency `get_current_user`
  - Rollen-Dependency `require_roles([...])`
- **Erste API-Module (Admin-Bereich)** umsetzen:
  - CRUD für **tool_categories**
  - CRUD für **tools**
  - CRUD für **tool_items** inkl. Status/Condition setzen
- **Workflow (MVP) vorbereiten/implementieren**:
  - **loan_requests** erstellen (Mitarbeiter)
  - **Approve/Reject** durch Abteilungsleiter der jeweiligen Abteilung
  - **Loan ausgeben** und **Rückgabe** erfassen (Admin/ausgebende Rolle)