# ============================================================
# api/router.py – Haupt-API-Router
#
# Sammelt alle einzelnen Router der Entitäten in einem zentralen Router.
# Dieser wird in main.py unter dem Prefix /api/v1 eingebunden,
# sodass alle Endpunkte unter /api/v1/<endpoint> erreichbar sind.
#
# Jede Entität hat eine eigene Router-Datei in api/routes/.
# ============================================================

from fastapi import APIRouter

# Alle Route-Module importieren
from src.app.api.routes.roles import router as roles_router
from src.app.api.routes.departments import router as departments_router
from src.app.api.routes.users import router as users_router
from src.app.api.routes.tool_categories import router as tool_categories_router
from src.app.api.routes.tool_statuses import router as tool_statuses_router
from src.app.api.routes.tool_conditions import router as tool_conditions_router
from src.app.api.routes.tools import router as tools_router
from src.app.api.routes.tool_items import router as tool_items_router
from src.app.api.routes.tool_item_issue_statuses import router as tool_item_issue_statuses_router
from src.app.api.routes.tool_item_issues import router as tool_item_issues_router
from src.app.api.routes.loan_request_statuses import router as loan_request_statuses_router
from src.app.api.routes.loan_requests import router as loan_requests_router
from src.app.api.routes.loans import router as loans_router
from src.app.api.routes.loan_items import router as loan_items_router
from src.app.api.routes.loan_request_items import router as loan_request_items_router

# Zentraler Router – in main.py eingebunden mit Prefix "/api/v1"
api_router = APIRouter()

# Benutzer & Verwaltung
api_router.include_router(roles_router)
api_router.include_router(departments_router)
api_router.include_router(users_router)

# Werkzeuge & Inventar (Lookup-Tabellen + Hauptentitäten)
api_router.include_router(tool_categories_router)
api_router.include_router(tool_statuses_router)
api_router.include_router(tool_conditions_router)
api_router.include_router(tools_router)
api_router.include_router(tool_items_router)

# Schadensberichte
api_router.include_router(tool_item_issue_statuses_router)
api_router.include_router(tool_item_issues_router)

# Ausleiheworkflow
api_router.include_router(loan_request_statuses_router)
api_router.include_router(loan_requests_router)
api_router.include_router(loans_router)
api_router.include_router(loan_items_router)
api_router.include_router(loan_request_items_router)
