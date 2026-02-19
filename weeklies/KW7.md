# Wochenbericht – KW 7 / 2026 (10.02.–16.02.2026)

> **Projekt:** Werkzeugverwaltungstool  
> **Ausbildung:** Fachinformatikerin für Anwendungsentwicklung  
> **Schwerpunkt der Woche:** Projektfindung, Planung & Anforderungsanalyse
> **Autorin:** Maila Anna Pgnari

---

## 🧭 Wochenziel
In dieser Woche wollte ich ein geeignetes Projekt für die IHK-Projektarbeit auswählen und die Grundlagen so vorbereiten, dass ich anschließend strukturiert mit der Umsetzung starten kann. Ziel war es, ein alltagsnahes Thema zu finden, den Funktionsumfang sinnvoll abzugrenenzen (MVP vs. Erweiterungen) und die wichtigsten Artefakte für die Projektplanung zu erstellen.

---

## ✅ Was ich diese Woche erreicht habe

### 1) Projektidee & Kontext
Ich habe mich für das Projekt **„Werkzeugverwaltungstool“** entschieden.  
Die Idee dahinter: In vielen Werkstätten oder Ausbildungsbereichen wird Werkzeugausgabe oft noch manuell über Listen/Excel dokumentiert. Dadurch ist nicht immer klar, **wer** ein Werkzeug hat, **wann** es zurück muss oder welche Ausleihen **überfällig** sind.

Mit dem Werkzeugverwaltungstool möchte ich eine webbasierte Lösung entwickeln, die:
- Werkzeuge (inkl. mehrerer Inventarstücke pro Werkzeugtyp) verwaltet,
- Ausleihen und Rückgaben nachvollziehbar dokumentiert,
- Ausleihanfragen über einen **Genehmigungsprozess** abwickelt,
- und durch Rollen/Rechte eine realistische Nutzung im Betrieb abbildet.

---

### 2) Planung & Anforderungen
Ich habe Anforderungen gesammelt und strukturiert – unter anderem:
- Rollen & Rechte (Admin / Abteilungsleiter / Mitarbeiter)
- Werkzeugverwaltung (Werkzeugtypen + Inventarstücke)
- Ausleihanfragen (mit Menge) & Genehmigung
- Ausleihe/Rückgabe (inkl. Zustandsdokumentation)
- Übersichten (z. B. aktive/überfällige Ausleihen)

Zusätzlich habe ich begonnen, Anforderungen in **MVP** und **Optionale Erweiterungen** zu unterteilen, um den Umfang realistisch in der verfügbaren Zeit umsetzen zu können.

---

### 3) Projektantrag (IHK)
Ich habe den **Projektantrag** erstellt und die Inhalte so formuliert, dass:
- das Ziel und der Nutzen klar verständlich sind,
- der Umfang realistisch abgegrenzt ist,
- sowie eine grobe Zeitplanung und die geplanten Projektphasen enthalten sind.

---

### 4) User Stories
Ich habe die wichtigsten Anforderungen als **User Stories** formuliert und priorisiert, inkl.:
- Akzeptanzkriterien (wann gilt eine Story als erledigt)
- grobe Aufwandsschätzung (Story Points)
- Business Value (Nutzenbewertung)
- Aufteilung in Product Goals (z. B. Rollen/Rechte, Workflow, Ausleihe/Rückgabe)

Das hilft mir jetzt dabei, die Umsetzung schrittweise und nachvollziehbar zu planen.

---

### 5) Use-Case-Diagramm
Auf Basis der User Stories habe ich ein **Use-Case-Diagramm** erstellt.  
Damit kann ich den Funktionsumfang anschaulich darstellen und die Rollen klar voneinander abgrenzen (z. B. wer darf genehmigen, wer darf Werkzeuge anlegen, wer darf ausleihen).

---

## 🧩 Artefakte / Ergebnisse der Woche
- ✅ Projektidee inkl. grober Zielsetzung und Nutzenbeschreibung  
- ✅ Anforderungsliste (funktional & nicht-funktional)  
- ✅ Projektantrag (IHK) – Entwurf/fertiggestellt  
- ✅ User Stories (inkl. Priorisierung & Akzeptanzkriterien)  
- ✅ Use-Case-Diagramm  

---

## 📌 Herausforderungen & Lösungen
- **Herausforderung:** Den Projektumfang realistisch halten (68h inkl. Doku & UML).  
  **Lösung:** Strikte Trennung in MVP vs. optionale Erweiterungen und klare Priorisierung über User Stories.

- **Herausforderung:** Genehmigungsworkflow fachlich sinnvoll abbilden.  
  **Lösung:** Genehmigung pro Abteilung über den Abteilungsleiter; Anfragen enthalten Positionen mit Mengen, Ausleihen referenzieren konkrete Inventarstücke.

---

## 🔭 Ausblick auf nächste Woche (KW 8)
Nächste Woche starte ich mit der technischen Umsetzung. Geplant ist:
- Datenbank finalisieren (Datenbankentwurf/Schema) und Migrationen vorbereiten
- Backend-Grundgerüst (FastAPI), Authentifizierung & Rollenprüfung
- Erste API-Endpunkte (Werkzeugtypen, Inventarstücke, Anfragen)

---

## 📝 Notizen
Die Woche war stark planungsorientiert. Ich habe bewusst Zeit in Struktur und Dokumente investiert, damit die Umsetzung später schneller und ohne größere Umplanungen funktioniert.