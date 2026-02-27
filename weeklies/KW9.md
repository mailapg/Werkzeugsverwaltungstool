# Wochenbericht – KW 9 / 2026 (23.02.–27.02.2026)

> **Projekt:** Werkzeugverwaltungstool
> **Ausbildung:** Fachinformatikerin für Anwendungsentwicklung
> **Schwerpunkt der Woche:** Authentifizierung, vollständige CRUD-Schicht, alle API-Endpunkte & Testsuite
> **Autorin:** Maila Anna Pignari

<br/>

## Was ich diese Woche gemacht habe
- **Authentifizierung:** JWT-Login eingebaut; Nutzer können sich einloggen und ausloggen, Endpunkte sind je nach Rolle geschützt.
- **CRUD-Schicht:** Für alle Entitäten (Nutzer, Abteilungen, Werkzeuge, Ausleihen usw.) komplette Erstellen/Lesen/Bearbeiten/Löschen-Funktionen umgesetzt.
- **API-Endpunkte:** Alle Endpunkte eingebunden, darunter auch Sonderfunktionen wie QR-Code-Generierung, überfällige Ausleihen und Abteilungsfilterung.
- **Testsuite:** Über 120 automatisierte Tests geschrieben, die alle Endpunkte und Sonderfälle abdecken.
- **Dokumentation:** Datenbankentwurf aktualisiert, User Stories überarbeitet und `requirements.txt` gepflegt.
- **Demo-Seed-Skript:** Skript erstellt, das die Datenbank mit realistischen Testdaten befüllt (Mitarbeiter, Werkzeuge, Ausleihen usw.).
- **Initial-Manager-Konfiguration:** Admin-Zugangsdaten können jetzt über Umgebungsvariablen gesetzt werden.
- **Tool-Backend:** Kleinere Korrekturen an Modell, CRUD-Schicht und Routen für Werkzeuge.
- **Abteilungsleiter-Logik:** Wird ein Nutzer als Abteilungsleiter eingesetzt oder entfernt, passt das System die Rollen automatisch an – der alte Leiter wird zurückgestuft, ein neuer zufällig ausgewählt.
- **Delete-Endpunkte:** Geben jetzt eine Bestätigungsnachricht zurück statt einer leeren Antwort.
- **Bugfixes:** Serverfehler bei `.local`-E-Mail-Adressen behoben; Nutzer können nicht mehr mit ungültigen Rollen oder Abteilungen angelegt werden.
- **`backend/static/`-Verzeichnis** angelegt für statische Dateien wie z. B. Werkzeugbilder.

<br/>

## 🔭 Ausblick auf nächste Woche (KW 10)
- **Frontend-Start** mit React + Tailwind CSS + shadcn/ui:
  - Projektsetup (Vite, Routing, Auth-Kontext)
  - Login-Seite und Auth-Flow (Token speichern, geschützte Routen)
  - Erste Übersichtsseite (z. B. Werkzeug-Liste)

