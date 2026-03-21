// ============================================================
// lib/labels.ts – Deutsche Beschriftungen für Enum-Werte
//
// Das Backend gibt Status-Werte auf Englisch zurück (z.B. "AVAILABLE").
// Diese Maps übersetzen diese in lesbare deutsche Texte für die UI.
//
// Verwendung:
//   import { toolStatusLabel, t } from '../lib/labels'
//   t(toolStatusLabel, item.status.name)  → "Verfügbar"
//   toolStatusLabel[item.status.name]     → "Verfügbar"
// ============================================================

// Rollenbezeichnungen
export const roleLabel: Record<string, string> = {
  ADMIN: 'Administrator',
  DEPARTMENT_MANAGER: 'Abteilungsleiter',
  EMPLOYEE: 'Mitarbeiter',
}

export const toolStatusLabel: Record<string, string> = {
  AVAILABLE: 'Verfügbar',
  LOANED: 'Ausgeliehen',
  DEFECT: 'Defekt',
  MAINTENANCE: 'Wartung',
  RETIRED: 'Ausgesondert',
}

export const toolConditionLabel: Record<string, string> = {
  OK: 'In Ordnung',
  WORN: 'Abgenutzt',
  DEFECT: 'Defekt',
}

export const loanRequestStatusLabel: Record<string, string> = {
  REQUESTED: 'Ausstehend',
  APPROVED: 'Genehmigt',
  REJECTED: 'Abgelehnt',
  CANCELLED: 'Abgebrochen',
}

export const issueStatusLabel: Record<string, string> = {
  OPEN: 'Offen',
  IN_PROGRESS: 'In Bearbeitung',
  RESOLVED: 'Gelöst',
  CLOSED: 'Geschlossen',
}

// Hilfsfunktion: Schlägt einen Schlüssel in einer Map nach.
// Gibt den Schlüssel selbst zurück, wenn kein Eintrag gefunden wird (Fallback).
export const t = (map: Record<string, string>, key: string) => map[key] ?? key
