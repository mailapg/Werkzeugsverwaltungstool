# ============================================================
# core/role_ids.py – Stabile Rollen-ID-Konstanten
#
# Diese IDs werden beim ersten Start der Anwendung (Seeding) in die
# Datenbank eingetragen. Die Reihenfolge und Werte dürfen sich NICHT
# ändern, da sie hart-kodiert in der Rollenprüfung verwendet werden.
#
# WICHTIG: Diese Werte müssen mit dem Frontend (AuthContext.tsx) übereinstimmen!
# ============================================================

ADMIN_ID = 1    # Vollzugriff auf alle Funktionen
MANAGER_ID = 2  # DEPARTMENT_MANAGER: Abteilung verwalten, Anträge genehmigen
EMPLOYEE_ID = 3 # Mitarbeiter: Ausleihen, Anträge stellen, Probleme melden
