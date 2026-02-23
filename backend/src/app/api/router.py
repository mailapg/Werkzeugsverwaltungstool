from fastapi import APIRouter

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

api_router = APIRouter()

api_router.include_router(roles_router)
api_router.include_router(departments_router)
api_router.include_router(users_router)
api_router.include_router(tool_categories_router)
api_router.include_router(tool_statuses_router)
api_router.include_router(tool_conditions_router)
api_router.include_router(tools_router)
api_router.include_router(tool_items_router)
api_router.include_router(tool_item_issue_statuses_router)
api_router.include_router(tool_item_issues_router)
api_router.include_router(loan_request_statuses_router)
api_router.include_router(loan_requests_router)
api_router.include_router(loans_router)
api_router.include_router(loan_items_router)
api_router.include_router(loan_request_items_router)
