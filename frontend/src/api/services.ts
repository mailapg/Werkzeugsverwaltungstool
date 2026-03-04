import api from './client'
import type { User, Department, Role, Tool, ToolItem, ToolItemHistoryEntry, ToolItemIssue, LoanRequest, Loan, ToolCategory, ToolStatus, ToolCondition, ToolItemIssueStatus, LoanRequestStatus } from '../types'

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: async (email: string, password: string) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const res = await api.post<{ access_token: string; token_type: string }>(
      '/auth/login',
      form,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    )
    return res.data
  },
  logout: () => api.post('/auth/logout'),
  me: () => api.get<User>('/api/v1/getusers').then(r => r.data),
}

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: () => api.get<User[]>('/api/v1/getusers').then(r => r.data),
  get: (id: number) => api.get<User>(`/api/v1/getuser/${id}`).then(r => r.data),
  create: (data: object) => api.post<User>('/api/v1/createuser', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<User>(`/api/v1/updateuser/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deleteuser/${id}`).then(r => r.data),
}

// ── Departments ───────────────────────────────────────────────────────────────
export const departmentsApi = {
  list: () => api.get<Department[]>('/api/v1/getdepartments').then(r => r.data),
  get: (id: number) => api.get<Department>(`/api/v1/getdepartment/${id}`).then(r => r.data),
  create: (data: object) => api.post<Department>('/api/v1/createdepartment', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<Department>(`/api/v1/updatedepartment/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deletedepartment/${id}`).then(r => r.data),
}

// ── Roles ─────────────────────────────────────────────────────────────────────
export const rolesApi = {
  list: () => api.get<Role[]>('/api/v1/getroles').then(r => r.data),
  create: (data: object) => api.post<Role>('/api/v1/createrole', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<Role>(`/api/v1/updaterole/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deleterole/${id}`).then(r => r.data),
}

// ── Tool Lookups ──────────────────────────────────────────────────────────────
export const lookupsApi = {
  categories: () => api.get<ToolCategory[]>('/api/v1/gettoolcategories').then(r => r.data),
  statuses: () => api.get<ToolStatus[]>('/api/v1/gettoolstatuses').then(r => r.data),
  conditions: () => api.get<ToolCondition[]>('/api/v1/gettoolconditions').then(r => r.data),
  issueStatuses: () => api.get<ToolItemIssueStatus[]>('/api/v1/gettoolitemissuestatuses').then(r => r.data),
  loanRequestStatuses: () => api.get<LoanRequestStatus[]>('/api/v1/getloanrequeststatuses').then(r => r.data),
  createCategory: (data: object) => api.post<ToolCategory>('/api/v1/createtoolcategory', data).then(r => r.data),
}

// ── Tools ─────────────────────────────────────────────────────────────────────
export const toolsApi = {
  list: () => api.get<Tool[]>('/api/v1/gettools').then(r => r.data),
  get: (id: number) => api.get<Tool>(`/api/v1/gettool/${id}`).then(r => r.data),
  create: (data: FormData) => api.post<Tool>('/api/v1/createtool', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data),
  update: (id: number, data: FormData) => api.patch<Tool>(`/api/v1/updatetool/${id}`, data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deletetool/${id}`).then(r => r.data),
}

// ── Tool Items ────────────────────────────────────────────────────────────────
export const toolItemsApi = {
  list: (params?: { tool_id?: number; status_id?: number }) =>
    api.get<ToolItem[]>('/api/v1/gettoolitems', { params }).then(r => r.data),
  get: (id: number) => api.get<ToolItem>(`/api/v1/gettoolitem/${id}`).then(r => r.data),
  create: (data: object) => api.post<ToolItem>('/api/v1/createtoolitem', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<ToolItem>(`/api/v1/updatetoolitem/${id}`, data).then(r => r.data),
  retire: (id: number) => api.patch<ToolItem>(`/api/v1/retiretoolitm/${id}`).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deletetoolitem/${id}`).then(r => r.data),
  history: (id: number) => api.get<ToolItemHistoryEntry[]>(`/api/v1/gettoolitemhistory/${id}`).then(r => r.data),
  qrCode: (id: number) => `http://localhost:8000/api/v1/gettoolitemqrcode/${id}`,
  qrCodeBlob: (id: number) => api.get(`/api/v1/gettoolitemqrcode/${id}`, { responseType: 'blob' }).then(r => URL.createObjectURL(r.data)),
}

// ── Issues ────────────────────────────────────────────────────────────────────
export const issuesApi = {
  list: () => api.get<ToolItemIssue[]>('/api/v1/gettoolitemissues').then(r => r.data),
  get: (id: number) => api.get<ToolItemIssue>(`/api/v1/gettoolitemissue/${id}`).then(r => r.data),
  create: (data: object) => api.post<ToolItemIssue>('/api/v1/createtoolitemissue', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<ToolItemIssue>(`/api/v1/updatetoolitemissue/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deletetoolitemissue/${id}`).then(r => r.data),
}

// ── Loan Requests ─────────────────────────────────────────────────────────────
export const loanRequestsApi = {
  list: () => api.get<LoanRequest[]>('/api/v1/getloanrequests').then(r => r.data),
  get: (id: number) => api.get<LoanRequest>(`/api/v1/getloanrequest/${id}`).then(r => r.data),
  create: (data: object) => api.post<LoanRequest>('/api/v1/createloanrequest', data).then(r => r.data),
  update: (id: number, data: object) => api.patch<LoanRequest>(`/api/v1/updateloanrequest/${id}`, data).then(r => r.data),
  decide: (id: number, data: object) => api.patch<LoanRequest>(`/api/v1/decideloanrequest/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deleteloanrequest/${id}`).then(r => r.data),
}

// ── Loans ─────────────────────────────────────────────────────────────────────
export const loansApi = {
  list: (params?: { active_only?: boolean }) =>
    api.get<Loan[]>('/api/v1/getloans', { params }).then(r => r.data),
  overdue: () => api.get<Loan[]>('/api/v1/getoverdueloans').then(r => r.data),
  get: (id: number) => api.get<Loan>(`/api/v1/getloan/${id}`).then(r => r.data),
  create: (data: object) => api.post<Loan>('/api/v1/createloan', data).then(r => r.data),
  return: (id: number, data: object) => api.patch<Loan>(`/api/v1/returnloan/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/v1/deleteloan/${id}`).then(r => r.data),
}
