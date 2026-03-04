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

export const t = (map: Record<string, string>, key: string) => map[key] ?? key
