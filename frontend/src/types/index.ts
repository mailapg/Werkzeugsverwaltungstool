export interface Role {
  id: number
  name: string
}

export interface Department {
  id: number
  name: string
  lead_user_id: number | null
}

export interface UserSlim {
  id: number
  firstname: string
  lastname: string
  email: string
}

export interface User {
  id: number
  firstname: string
  lastname: string
  email: string
  is_active: boolean
  role_id: number
  department_id: number
  role: Role
  department: Department
  created_at: string
  updated_at: string
}

export interface ToolCategory {
  id: number
  name: string
}

export interface ToolStatus {
  id: number
  name: string
}

export interface ToolCondition {
  id: number
  name: string
}

export interface Tool {
  id: number
  tool_name: string
  description: string | null
  category_id: number
  category: ToolCategory
  image_filename: string | null
}

export interface ToolItem {
  id: number
  inventory_no: string
  description: string | null
  tool_id: number
  tool: Tool
  status_id: number
  status: ToolStatus
  condition_id: number
  condition: ToolCondition
}

export interface ToolItemIssueStatus {
  id: number
  name: string
}

export interface ToolItemIssue {
  id: number
  tool_item_id: number
  tool_item: ToolItem
  reported_by_user_id: number
  reported_by: UserSlim
  status_id: number
  status: ToolItemIssueStatus
  title: string
  description: string | null
  reported_at: string
  resolved_at: string | null
}

export interface LoanRequestStatus {
  id: number
  name: string
}

export interface LoanRequestItem {
  id: number
  request_id: number
  tool_id: number
  tool: Tool
  quantity: number
}

export interface LoanRequest {
  id: number
  requester_user_id: number
  requester: UserSlim
  approver_user_id: number | null
  approver: UserSlim | null
  request_status_id: number
  status: LoanRequestStatus
  due_at: string | null
  days_needed: number | null
  requested_at: string
  decision_at: string | null
  decision_comment: string | null
  comment: string | null
  items: LoanRequestItem[]
}

export interface LoanItem {
  id: number
  loan_id: number
  tool_item_id: number
  tool_item: ToolItem
  return_condition_id: number | null
  return_condition: ToolCondition | null
  return_comment: string | null
}

export interface Loan {
  id: number
  issued_at: string
  due_at: string
  returned_at: string | null
  borrower_user_id: number
  borrower: UserSlim
  issued_by_user_id: number
  issuer: UserSlim
  returned_by_user_id: number | null
  return_processor: UserSlim | null
  comment: string | null
  items: LoanItem[]
  is_overdue: boolean
}

export interface ToolItemHistoryEntry {
  loan_id: number
  borrower: UserSlim
  issued_at: string
  due_at: string
  returned_at: string | null
  return_condition: ToolCondition | null
  return_comment: string | null
}

export interface AuthUser {
  id: number
  role_id: number
  department_id: number
}
