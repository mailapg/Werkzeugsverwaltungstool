from src.app.schemas.role import RoleCreate, RoleUpdate, RoleRead
from src.app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
from src.app.schemas.user import UserCreate, UserUpdate, UserRead, UserSlim
from src.app.schemas.tool_category import ToolCategoryCreate, ToolCategoryUpdate, ToolCategoryRead
from src.app.schemas.tool_status import ToolStatusCreate, ToolStatusUpdate, ToolStatusRead
from src.app.schemas.tool_condition import ToolConditionCreate, ToolConditionUpdate, ToolConditionRead
from src.app.schemas.tool import ToolCreate, ToolUpdate, ToolRead
from src.app.schemas.tool_item import ToolItemCreate, ToolItemUpdate, ToolItemRead, ToolItemSlim
from src.app.schemas.tool_item_issue_status import ToolItemIssueStatusCreate, ToolItemIssueStatusUpdate, ToolItemIssueStatusRead
from src.app.schemas.tool_item_issue import ToolItemIssueCreate, ToolItemIssueUpdate, ToolItemIssueRead
from src.app.schemas.loan_request_status import LoanRequestStatusCreate, LoanRequestStatusUpdate, LoanRequestStatusRead
from src.app.schemas.loan_request_item import LoanRequestItemCreate, LoanRequestItemUpdate, LoanRequestItemRead
from src.app.schemas.loan_request import LoanRequestCreate, LoanRequestUpdate, LoanRequestRead
from src.app.schemas.loan_item import LoanItemCreate, LoanItemUpdate, LoanItemRead
from src.app.schemas.loan import LoanCreate, LoanUpdate, LoanRead

__all__ = [
    "RoleCreate", "RoleUpdate", "RoleRead", "DepartmentCreate", "DepartmentUpdate", "DepartmentRead", "UserCreate", "UserUpdate", "UserRead", "UserSlim",
    "ToolCategoryCreate", "ToolCategoryUpdate", "ToolCategoryRead", "ToolStatusCreate", "ToolStatusUpdate", "ToolStatusRead",
    "ToolConditionCreate", "ToolConditionUpdate", "ToolConditionRead", "ToolCreate", "ToolUpdate", "ToolRead", "ToolItemCreate",
    "ToolItemUpdate", "ToolItemRead", "ToolItemSlim","ToolItemIssueStatusCreate", "ToolItemIssueStatusUpdate", "ToolItemIssueStatusRead",
    "ToolItemIssueCreate", "ToolItemIssueUpdate", "ToolItemIssueRead", "LoanRequestStatusCreate", "LoanRequestStatusUpdate", "LoanRequestStatusRead",
    "LoanRequestItemCreate", "LoanRequestItemUpdate", "LoanRequestItemRead", "LoanRequestCreate", "LoanRequestUpdate", "LoanRequestRead",
    "LoanItemCreate", "LoanItemUpdate", "LoanItemRead", "LoanCreate", "LoanUpdate", "LoanRead"
]