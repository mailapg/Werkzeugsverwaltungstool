"""
Demo-Seed: Befüllt die Datenbank mit realistischen Testdaten.

Aufruf aus dem backend/ Verzeichnis:
    python -m src.app.seed.seed_demo

Erstellt:
  - 1 Admin (admin@admin.local / admin)
  - 12 Abteilungen mit je 1 Abteilungsleiter
  - 55 Mitarbeiter
  - 63 Werkzeugtypen → 309 Exemplare
  - Ausleiheanfragen, Ausleihen, Issues

ACHTUNG: Löscht und überschreibt alle bestehenden Daten.
"""

import os
import random
from datetime import datetime, timezone, timedelta

os.environ.setdefault("JWT_SECRET_KEY", "demo-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("SEED_MANAGER_EMAIL", "seed@local")
os.environ.setdefault("SEED_MANAGER_PASSWORD", "seed")
os.environ.setdefault("SEED_MANAGER_FIRSTNAME", "Seed")
os.environ.setdefault("SEED_MANAGER_LASTNAME", "User")

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.app.db.session import engine
from src.app.db.base import Base
import src.app.models  # noqa – alle Modelle registrieren

from src.app.models.role import Role
from src.app.models.department import Department
from src.app.models.user import User
from src.app.models.tool_category import ToolCategory
from src.app.models.tool_status import ToolStatus
from src.app.models.tool_condition import ToolCondition
from src.app.models.tool import Tool
from src.app.models.tool_item import ToolItem
from src.app.models.tool_item_issue_status import ToolItemIssueStatus
from src.app.models.tool_item_issue import ToolItemIssue
from src.app.models.loan_request_status import LoanRequestStatus
from src.app.models.loan_request import LoanRequest
from src.app.models.loan_request_item import LoanRequestItem
from src.app.models.loan import Loan
from src.app.models.loan_item import LoanItem

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
rng = random.Random(42)
UTC = timezone.utc


def now() -> datetime:
    return datetime.now(tz=UTC)


def past(days: int = 0, hours: int = 0) -> datetime:
    return now() - timedelta(days=days, hours=hours)


def future(days: int) -> datetime:
    return now() + timedelta(days=days)


def normalize(name: str) -> str:
    """Umlaute und Sonderzeichen für E-Mail-Adressen entfernen."""
    return (
        name.lower()
        .replace("ü", "ue")
        .replace("ö", "oe")
        .replace("ä", "ae")
        .replace("ß", "ss")
        .replace(" ", "")
        .replace("-", "")
    )


def make_email(firstname: str, lastname: str, domain: str, used: set) -> str:
    base = normalize(firstname[0]) + normalize(lastname)
    candidate = f"{base}@{domain}.local"
    if candidate not in used:
        used.add(candidate)
        return candidate
    for i in range(2, 20):
        candidate = f"{base}{i}@{domain}.local"
        if candidate not in used:
            used.add(candidate)
            return candidate
    raise ValueError(f"Kein eindeutiger E-Mail für {firstname} {lastname}")


# ---------------------------------------------------------------------------
# Stammdaten
# ---------------------------------------------------------------------------

DEPARTMENT_DATA = [
    ("Werkstatt",          "werkstatt"),
    ("Lager",              "lager"),
    ("Elektro",            "elektro"),
    ("Schlosserei",        "schlosserei"),
    ("Hydraulik",          "hydraulik"),
    ("Pneumatik",          "pneumatik"),
    ("Messtechnik",        "messtechnik"),
    ("Schweißerei",        "schweisserei"),
    ("Montage",            "montage"),
    ("Instandhaltung",     "instandhaltung"),
    ("Fertigung",          "fertigung"),
    ("Qualitätssicherung", "qualitaet"),
]

# (Vorname, Nachname) – erste 12 werden Abteilungsleiter, Rest Mitarbeiter
PERSONS = [
    # Abteilungsleiter (12)
    ("Klaus",     "Müller"),
    ("Werner",    "Schmidt"),
    ("Thomas",    "Fischer"),
    ("Andreas",   "Weber"),
    ("Stefan",    "Meyer"),
    ("Michael",   "Wagner"),
    ("Peter",     "Becker"),
    ("Robert",    "Schulz"),
    ("Markus",    "Hoffmann"),
    ("Christian", "Koch"),
    ("Sabine",    "Richter"),
    ("Monika",    "Klein"),
    # Mitarbeiter (55)
    ("Daniel",    "Wolf"),
    ("Tobias",    "Schröder"),
    ("Sebastian", "Neumann"),
    ("Florian",   "Schwarz"),
    ("Martin",    "Zimmermann"),
    ("Jochen",    "Braun"),
    ("Frank",     "Krüger"),
    ("Georg",     "Hofmann"),
    ("Ralf",      "Hartmann"),
    ("Karl",      "Lange"),
    ("Bernd",     "Schmitt"),
    ("Dieter",    "Werner"),
    ("Helmut",    "Krause"),
    ("Ulrich",    "Roth"),
    ("Manfred",   "Kern"),
    ("Jürgen",    "Maier"),
    ("Walter",    "Huber"),
    ("Horst",     "Kaiser"),
    ("Wolfgang",  "Fuchs"),
    ("Lars",      "Herrmann"),
    ("Jan",       "Lang"),
    ("Kai",       "Möller"),
    ("Patrick",   "Vogt"),
    ("Oliver",    "Sauer"),
    ("Sven",      "Engel"),
    ("Dennis",    "Brandt"),
    ("Kevin",     "Berger"),
    ("Marcel",    "Ziegler"),
    ("Tim",       "Frank"),
    ("Petra",     "Wittig"),
    ("Karin",     "Baumann"),
    ("Claudia",   "Franke"),
    ("Julia",     "Albrecht"),
    ("Lisa",      "Winter"),
    ("Anna",      "Lehmann"),
    ("Maria",     "Groß"),
    ("Christine", "Hahn"),
    ("Sandra",    "Krämer"),
    ("Nicole",    "Böhm"),
    ("Melanie",   "Schreiber"),
    ("Jessica",   "König"),
    ("Stefanie",  "Bauer"),
    ("Brigitte",  "Vogel"),
    ("Heike",     "Günther"),
    ("Inge",      "Schäfer"),
    ("Renate",    "Ludwig"),
    ("Silvia",    "Keller"),
    ("Nadine",    "Lorenz"),
    ("Katrin",    "Weiß"),
    ("Simone",    "Beck"),
    ("Birgit",    "Zimmermann"),
    ("Leon",      "Müller"),
    ("Lena",      "Schmidt"),
    ("Felix",     "Braun"),
    ("Hannah",    "Koch"),
]

# (Werkzeugname, Beschreibung, Kategorie, Anzahl Exemplare)
TOOL_DATA = [
    # Schlagwerkzeug
    ("Schlosserhammer 500g",        "Schlosserhammer für Allgemeinarbeiten",          "Schlagwerkzeug",  8),
    ("Schlosserhammer 300g",        "Leichter Schlosserhammer für Feinarbeiten",      "Schlagwerkzeug",  6),
    ("Vorschlaghammer 2kg",         "Schwerer Aufbruchhammer",                        "Schlagwerkzeug",  4),
    ("Vorschlaghammer 5kg",         "Extra schwerer Abbruchhammer",                   "Schlagwerkzeug",  3),
    ("Gummihammer",                 "Schonhammer für empfindliche Oberflächen",       "Schlagwerkzeug",  6),
    ("Klauenhammer",                "Zimmermannshammer mit Nagelzieher",              "Schlagwerkzeug",  4),
    # Handwerkzeug / Zangen
    ("Kombizange",                  "Universal-Kombizange 180mm",                     "Handwerkzeug",    8),
    ("Flachzange",                  "Präzisionsflachzange 150mm",                     "Handwerkzeug",    6),
    ("Spitzzange",                  "Spitzzange für enge Stellen",                    "Handwerkzeug",    6),
    ("Seitenschneider",             "Seitenschneider 160mm",                          "Handwerkzeug",    7),
    ("Wasserpumpenzange",           "Wasserpumpenzange 250mm verstellbar",            "Handwerkzeug",    5),
    ("Rohrzange",                   "Rohrzange 315mm",                                "Handwerkzeug",    4),
    ("Kneifzange",                  "Kneifzange für Nagelentfernung",                 "Handwerkzeug",    4),
    # Schraubwerkzeug
    ("Kreuzschlitz-Schraubendreher PH1",  "Präziser PH1 Schraubendreher",            "Schraubwerkzeug", 8),
    ("Kreuzschlitz-Schraubendreher PH2",  "Standard PH2 Schraubendreher",            "Schraubwerkzeug", 10),
    ("Schlitz-Schraubendreher 5mm",       "Schlitzschraubendreher 5mm Klinge",       "Schraubwerkzeug", 7),
    ("Torx-Schraubendreher T20",          "Torx T20 Schraubendreher",                "Schraubwerkzeug", 5),
    ("Torx-Schraubendreher T30",          "Torx T30 Schraubendreher",                "Schraubwerkzeug", 5),
    ("Gabelschlüssel-Satz 8-19mm",        "6-teiliger Gabelschlüsselsatz",           "Schraubwerkzeug", 6),
    ("Ringschlüssel-Satz 8-19mm",         "6-teiliger Ringschlüsselsatz",            "Schraubwerkzeug", 5),
    ('Steckschlüsselsatz 1/2"',           "21-teiliger Steckschlüsselsatz",          "Schraubwerkzeug", 5),
    ('Steckschlüsselsatz 1/4"',           "26-teiliger Steckschlüsselsatz",          "Schraubwerkzeug", 4),
    ("Drehmomentschlüssel 20-200Nm",      "Klick-Drehmomentschlüssel",               "Schraubwerkzeug", 4),
    ("Inbus-Schlüsselsatz metrisch",      "9-teiliger Inbus-Satz metrisch",          "Schraubwerkzeug", 6),
    # Bohrwerkzeug
    ("Akkubohrschrauber 18V",       "18V Akkubohrschrauber mit 2 Akkus",              "Bohrwerkzeug",    8),
    ("Schlagbohrmaschine 800W",     "Schlagbohrmaschine für Mauerwerk",               "Bohrwerkzeug",    6),
    ("Bohrhammer SDS-Plus",         "SDS-Plus Bohrhammer für Beton",                  "Bohrwerkzeug",    4),
    ("Winkelbohraufsatz",           "90-Grad-Winkelaufsatz für Bohrmaschine",         "Bohrwerkzeug",    3),
    # Sägewerkzeug
    ("Handsäge",                    "Universalsäge 500mm",                            "Sägewerkzeug",    5),
    ("Bügelsäge",                   "Bügelsäge für Metall",                           "Sägewerkzeug",    4),
    ("Stichsäge",                   "Elektrische Stichsäge 700W",                     "Sägewerkzeug",    5),
    ("Kreissäge",                   "Handkreissäge 1400W",                            "Sägewerkzeug",    3),
    ("Säbelsäge",                   "Elektrische Säbelsäge für grobe Schnitte",       "Sägewerkzeug",    3),
    # Schleifwerkzeug
    ("Winkelschleifer 115mm",       "Winkelschleifer 900W",                           "Schleifwerkzeug", 6),
    ("Winkelschleifer 125mm",       "Winkelschleifer 1200W",                          "Schleifwerkzeug", 5),
    ("Schwingschleifer",            "Elektrischer Schwingschleifer 180W",             "Schleifwerkzeug", 4),
    ("Bandschleifer",               "Elektrischer Bandschleifer 850W",                "Schleifwerkzeug", 3),
    # Messgeräte
    ("Messschieber digital",        "Digitaler Messschieber 150mm",                   "Messgeräte",      6),
    ("Messschieber analog",         "Analoger Messschieber 150mm",                    "Messgeräte",      5),
    ("Wasserwaage 60cm",            "Aluminiumrahmen-Wasserwaage 60cm",               "Messgeräte",      6),
    ("Wasserwaage 120cm",           "Aluminiumrahmen-Wasserwaage 120cm",              "Messgeräte",      4),
    ("Maßband 5m",                  "Rollmaßband 5m",                                 "Messgeräte",      10),
    ("Maßband 10m",                 "Rollmaßband 10m",                                "Messgeräte",      5),
    ("Multimeter digital",          "Digitales Multimeter 600V AC/DC",                "Messgeräte",      6),
    ("Drehmomentprüfer digital",    "Digitaler Drehmomentprüfer",                     "Messgeräte",      3),
    # Elektrowerkzeug
    ("Heißluftpistole 2000W",       "Heißluftpistole mit Temperaturregelung",         "Elektrowerkzeug", 4),
    ("Lötkolben 40W",               "Lötkolben für Elektronikarbeiten",               "Elektrowerkzeug", 5),
    ("Lötstation digital",          "Digitale Lötstation mit Temperaturregelung",     "Elektrowerkzeug", 3),
    ("Elektrotacker",               "Elektrischer Tacker für Kabelbefestigung",       "Elektrowerkzeug", 3),
    # Schneidwerkzeug
    ("Cuttermesser 18mm",           "Abbrechmesser 18mm",                             "Schneidwerkzeug", 10),
    ("Metall-Feile flach",          "Flachfeile Hieb 2, 200mm",                       "Schneidwerkzeug", 6),
    ("Metall-Feile rund",           "Rundfeile Hieb 2, 200mm",                        "Schneidwerkzeug", 5),
    ("Meißel flach 20mm",           "Flachmeißel 200mm",                              "Schneidwerkzeug", 6),
    ("Meißel rund 16mm",            "Rundmeißel 200mm",                               "Schneidwerkzeug", 4),
    # Schweißzubehör
    ("MIG/MAG Schweißgerät 230V",   "MIG/MAG Schweißgerät für Stahl und Edelstahl",  "Schweißzubehör",  3),
    ("WIG Schweißgerät 200A",       "WIG/TIG Schweißgerät 200A",                      "Schweißzubehör",  2),
    ("Schweißschutzschild",         "Automatisches Schweißschutzschild",              "Schweißzubehör",  5),
    # Spanntechnik
    ("Hydraulikheber 2t",           "Rangierwagenheber 2 Tonnen",                     "Spanntechnik",    3),
    ("Schraubzwinge 150mm",         "Tiefspann-Schraubzwinge 150mm",                  "Spanntechnik",    8),
    ("Schraubzwinge 300mm",         "Tiefspann-Schraubzwinge 300mm",                  "Spanntechnik",    6),
]

ISSUE_DATA = [
    ("Griff gebrochen",             "Der Kunststoffgriff ist vollständig gebrochen."),
    ("Kalibrierung notwendig",      "Messergebnis weicht um mehr als 0,5mm ab."),
    ("Akku hält nicht mehr",        "Akku entlädt sich innerhalb von 20 Minuten."),
    ("Schneide stumpf",             "Klinge schneidet nicht mehr sauber."),
    ("Gehäuse gerissen",            "Sichtbarer Riss im Gehäuse, Sicherheitsrisiko."),
    ("Schutzvorrichtung beschädigt","Schutzabdeckung lässt sich nicht mehr fixieren."),
    ("Kabel beschädigt",            "Isolierung des Netzkabels ist eingerissen."),
    ("Rost an Metallfläche",        "Starke Rostbildung an Griffbereich."),
    ("Gewindegänge beschädigt",     "Einstellschraube dreht durch."),
    ("Display defekt",              "Display zeigt nur noch Striche an."),
    ("Schraube fehlt",              "Befestigungsschraube am Gehäuse fehlt."),
    ("Klingenverschleiß",           "Sägeblatt deutlich abgenutzt, Schnittleistung reduziert."),
    ("Überhitzungsschaden",         "Gerät schaltet nach kurzer Zeit wegen Überhitzung ab."),
    ("Lager defekt",                "Deutlich hörbares Schleifen beim Betrieb."),
    ("Aufsatz fehlt",               "Schutzaufsatz nicht mehr vorhanden."),
]


# ---------------------------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------------------------

def run_demo_seed():
    print("Datenbank wird zurückgesetzt...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tabellen erstellt.")

    with Session(engine) as db:
        # --- 1. Rollen
        role_admin  = Role(name="ADMIN")
        role_mgr    = Role(name="DEPARTMENT_MANAGER")
        role_emp    = Role(name="EMPLOYEE")
        db.add_all([role_admin, role_mgr, role_emp])
        db.flush()

        # --- 2. ToolStatus
        status_map = {}
        for name in ["AVAILABLE", "LOANED", "DEFECT", "MAINTENANCE", "RETIRED"]:
            s = ToolStatus(name=name)
            db.add(s)
            db.flush()
            status_map[name] = s

        # --- 3. ToolCondition
        cond_map = {}
        for name in ["OK", "WORN", "DEFECT"]:
            c = ToolCondition(name=name)
            db.add(c)
            db.flush()
            cond_map[name] = c

        # --- 4. LoanRequestStatus
        loan_req_status_map = {}
        for name in ["REQUESTED", "APPROVED", "REJECTED", "CANCELLED"]:
            lrs = LoanRequestStatus(name=name)
            db.add(lrs)
            db.flush()
            loan_req_status_map[name] = lrs

        # --- 5. ToolItemIssueStatus
        issue_status_map = {}
        for name in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]:
            iss = ToolItemIssueStatus(name=name)
            db.add(iss)
            db.flush()
            issue_status_map[name] = iss

        # --- 6. ToolCategories
        cat_map = {}
        for name in sorted(set(row[2] for row in TOOL_DATA)):
            cat = ToolCategory(name=name)
            db.add(cat)
            db.flush()
            cat_map[name] = cat

        print(f"  {len(cat_map)} Kategorien erstellt.")

        # --- 7. Abteilungen (ohne Leiter)
        dept_list = []
        for (dept_name, _domain) in DEPARTMENT_DATA:
            dept = Department(name=dept_name)
            db.add(dept)
            db.flush()
            dept_list.append(dept)

        print(f"  {len(dept_list)} Abteilungen erstellt.")

        # --- 8. Admin
        used_emails = set()
        admin = User(
            firstname="Admin",
            lastname="Admin",
            email="admin@admin.local",
            passwordhash=pwd_ctx.hash("admin"),
            role_id=role_admin.id,
            department_id=dept_list[0].id,
            is_active=True,
        )
        used_emails.add("admin@admin.local")
        db.add(admin)
        db.flush()
        print("  Admin-Nutzer erstellt (admin@admin.local / admin).")

        # --- 9. Abteilungsleiter (erste 12 Personen, je einer pro Abteilung)
        managers = []
        manager_persons = PERSONS[:12]
        for i, (fname, lname) in enumerate(manager_persons):
            dept = dept_list[i]
            domain = DEPARTMENT_DATA[i][1]
            email = make_email(fname, lname, domain, used_emails)
            mgr = User(
                firstname=fname,
                lastname=lname,
                email=email,
                passwordhash=pwd_ctx.hash("Passwort1!"),
                role_id=role_mgr.id,
                department_id=dept.id,
                is_active=True,
            )
            db.add(mgr)
            db.flush()
            dept.lead_user_id = mgr.id
            managers.append(mgr)

        print(f"  {len(managers)} Abteilungsleiter erstellt.")

        # --- 10. Mitarbeiter (restliche Personen)
        employees = []
        employee_persons = PERSONS[12:]
        for i, (fname, lname) in enumerate(employee_persons):
            dept = dept_list[i % len(dept_list)]
            domain = DEPARTMENT_DATA[i % len(DEPARTMENT_DATA)][1]
            email = make_email(fname, lname, domain, used_emails)
            emp = User(
                firstname=fname,
                lastname=lname,
                email=email,
                passwordhash=pwd_ctx.hash("Passwort1!"),
                role_id=role_emp.id,
                department_id=dept.id,
                is_active=True,
            )
            db.add(emp)
            db.flush()
            employees.append(emp)

        print(f"  {len(employees)} Mitarbeiter erstellt.")

        # --- 11. Werkzeuge und Exemplare
        all_tool_items = []
        inv_counter = 1
        tools_created = 0

        for (tool_name, description, cat_name, qty) in TOOL_DATA:
            tool = Tool(
                tool_name=tool_name,
                description=description,
                category_id=cat_map[cat_name].id,
            )
            db.add(tool)
            db.flush()
            tools_created += 1

            for _ in range(qty):
                inv_no = f"INV-{inv_counter:04d}"
                inv_counter += 1

                # Zufällige Verteilung: 85% AVAILABLE, 8% LOANED, 4% DEFECT, 3% MAINTENANCE
                r = rng.random()
                if r < 0.85:
                    status = status_map["AVAILABLE"]
                    cond_name = rng.choices(["OK", "OK", "OK", "WORN"], k=1)[0]
                elif r < 0.93:
                    status = status_map["LOANED"]
                    cond_name = "OK"
                elif r < 0.97:
                    status = status_map["DEFECT"]
                    cond_name = "DEFECT"
                else:
                    status = status_map["MAINTENANCE"]
                    cond_name = "WORN"

                item = ToolItem(
                    inventory_no=inv_no,
                    description=f"Exemplar #{inv_counter - 1} – {tool_name}",
                    tool_id=tool.id,
                    status_id=status.id,
                    condition_id=cond_map[cond_name].id,
                )
                db.add(item)
                db.flush()
                all_tool_items.append(item)

        print(f"  {tools_created} Werkzeugtypen und {len(all_tool_items)} Exemplare erstellt.")

        # --- 12. Aktive Ausleihen (für Exemplare im Status LOANED)
        loaned_items = [i for i in all_tool_items if i.status_id == status_map["LOANED"].id]
        all_users = managers + employees
        active_loans = []

        for item in loaned_items:
            borrower = rng.choice(all_users)
            issuer   = rng.choice(managers)
            issued_days_ago = rng.randint(1, 14)
            due_days = rng.randint(1, 10)

            loan = Loan(
                issued_at=past(days=issued_days_ago),
                due_at=future(days=due_days),
                borrower_user_id=borrower.id,
                issued_by_user_id=issuer.id,
                comment=rng.choice([None, None, "Für Reparaturauftrag", "Projektarbeit", "Maschinenwartung"]),
            )
            db.add(loan)
            db.flush()

            loan_item = LoanItem(loan_id=loan.id, tool_item_id=item.id)
            db.add(loan_item)
            active_loans.append(loan)

        print(f"  {len(active_loans)} aktive Ausleihen erstellt.")

        # --- 13. Abgeschlossene Ausleihen (historisch)
        available_items = [i for i in all_tool_items if i.status_id == status_map["AVAILABLE"].id]
        returned_loans_count = 0

        for item in rng.sample(available_items, min(60, len(available_items))):
            borrower = rng.choice(all_users)
            issuer   = rng.choice(managers)
            returner = rng.choice(managers)
            start_days = rng.randint(20, 90)
            duration   = rng.randint(1, 14)

            loan = Loan(
                issued_at=past(days=start_days),
                due_at=past(days=start_days - duration - 2),
                returned_at=past(days=start_days - duration),
                borrower_user_id=borrower.id,
                issued_by_user_id=issuer.id,
                returned_by_user_id=returner.id,
                comment=rng.choice([None, None, "Regelmäßige Wartung", "Projekteinsatz", None]),
            )
            db.add(loan)
            db.flush()

            return_cond = rng.choice(["OK", "OK", "OK", "WORN", "DEFECT"])
            loan_item = LoanItem(
                loan_id=loan.id,
                tool_item_id=item.id,
                return_condition_id=cond_map[return_cond].id,
                return_comment=rng.choice([None, None, "Leichte Gebrauchsspuren", "Sauber zurückgegeben", None]),
            )
            db.add(loan_item)
            returned_loans_count += 1

        print(f"  {returned_loans_count} abgeschlossene Ausleihen erstellt.")

        # --- 14. Ausleiheanfragen
        req_items_pool = rng.sample(available_items, min(40, len(available_items)))
        tool_ids_pool = list({i.tool_id for i in req_items_pool})
        req_count = 0

        # Offene Anfragen (REQUESTED)
        for _ in range(15):
            requester = rng.choice(employees)
            due = future(rng.randint(3, 21))
            tools_for_req = rng.sample(tool_ids_pool, rng.randint(1, 3))

            req = LoanRequest(
                requester_user_id=requester.id,
                request_status_id=loan_req_status_map["REQUESTED"].id,
                due_at=due,
                requested_at=past(days=rng.randint(1, 5)),
                comment=rng.choice([None, "Dringend benötigt", "Für Montageprojekt", None]),
            )
            db.add(req)
            db.flush()
            for tool_id in tools_for_req:
                ri = LoanRequestItem(request_id=req.id, tool_id=tool_id, quantity=rng.randint(1, 2))
                db.add(ri)
            req_count += 1

        # Abgelehnte Anfragen
        for _ in range(8):
            requester = rng.choice(employees)
            approver  = rng.choice(managers)
            decided_days_ago = rng.randint(2, 30)
            tools_for_req = rng.sample(tool_ids_pool, rng.randint(1, 2))

            req = LoanRequest(
                requester_user_id=requester.id,
                approver_user_id=approver.id,
                request_status_id=loan_req_status_map["REJECTED"].id,
                due_at=past(days=decided_days_ago - 5),
                requested_at=past(days=decided_days_ago + 3),
                decision_at=past(days=decided_days_ago),
                decision_comment=rng.choice([
                    "Werkzeug momentan nicht verfügbar.",
                    "Anfrage unvollständig.",
                    "Bitte direkt beim Lager anfragen.",
                ]),
            )
            db.add(req)
            db.flush()
            for tool_id in tools_for_req:
                ri = LoanRequestItem(request_id=req.id, tool_id=tool_id, quantity=1)
                db.add(ri)
            req_count += 1

        print(f"  {req_count} Ausleiheanfragen erstellt.")

        # --- 15. Tool-Item-Issues
        defect_and_maintenance = [
            i for i in all_tool_items
            if i.status_id in (status_map["DEFECT"].id, status_map["MAINTENANCE"].id)
        ]
        issue_pool = defect_and_maintenance + rng.sample(available_items, min(10, len(available_items)))
        issue_count = 0

        for item in rng.sample(issue_pool, min(25, len(issue_pool))):
            reporter = rng.choice(all_users)
            title, desc = rng.choice(ISSUE_DATA)
            is_resolved = rng.random() < 0.4

            status_name = rng.choice(["OPEN", "IN_PROGRESS"]) if not is_resolved else rng.choice(["RESOLVED", "CLOSED"])
            reported_days = rng.randint(1, 60)

            issue = ToolItemIssue(
                tool_item_id=item.id,
                reported_by_user_id=reporter.id,
                status_id=issue_status_map[status_name].id,
                title=title,
                description=desc,
                reported_at=past(days=reported_days),
                resolved_at=past(days=rng.randint(1, reported_days)) if is_resolved else None,
            )
            db.add(issue)
            issue_count += 1

        print(f"  {issue_count} Issues erstellt.")

        db.commit()

    # Zusammenfassung
    print("\n" + "=" * 55)
    print("  Demo-Seed erfolgreich abgeschlossen!")
    print("=" * 55)
    print(f"  Admin:           admin@admin.local  /  admin")
    print(f"  Manager-PW:      Passwort1!")
    print(f"  Mitarbeiter-PW:  Passwort1!")
    print(f"  Abteilungen:     {len(dept_list)}")
    print(f"  Abteilungsleiter:{len(managers)}")
    print(f"  Mitarbeiter:     {len(employees)}")
    print(f"  Werkzeugtypen:   {tools_created}")
    print(f"  Exemplare:       {len(all_tool_items)}")
    print("=" * 55)


if __name__ == "__main__":
    run_demo_seed()
