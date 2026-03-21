import { Page, Route } from '@playwright/test'

// ── JWT tokens (payload-only, no real signature – jwtDecode doesn't verify) ──
export const TOKENS = {
  admin:    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZV9pZCI6MSwiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature',
  manager:  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwicm9sZV9pZCI6MiwiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature',
  employee: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZV9pZCI6MywiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature',
}

/** Inject a token into localStorage so the app thinks we're logged in. */
export async function loginAs(page: Page, role: keyof typeof TOKENS) {
  await page.goto('/login')
  await page.evaluate((token) => localStorage.setItem('token', token), TOKENS[role])
}

/** Shorthand JSON response helper for page.route() */
export function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

// ── Shared mock data (field names match types/index.ts exactly) ──────────────
const CATEGORY_HW = { id: 1, name: 'Handwerkzeug' }
const CATEGORY_EL = { id: 2, name: 'Elektrowerkzeug' }

const TOOL_HAMMER: Record<string, unknown> = {
  id: 1, tool_name: 'Hammer', description: 'Stahlhammer 500g',
  category_id: 1, category: CATEGORY_HW, image_filename: null,
}
const TOOL_BOHR: Record<string, unknown> = {
  id: 2, tool_name: 'Bohrmaschine', description: 'Elektrisch 750W',
  category_id: 2, category: CATEGORY_EL, image_filename: null,
}

const STATUS_AVAIL  = { id: 1, name: 'AVAILABLE' }
const STATUS_LOANED = { id: 2, name: 'LOANED' }
const COND_OK   = { id: 1, name: 'OK' }
const COND_WORN = { id: 2, name: 'WORN' }

const ITEM_1 = {
  id: 1, inventory_no: 'INV-0001', description: null,
  tool_id: 1, tool: TOOL_HAMMER,
  status_id: 1, status: STATUS_AVAIL,
  condition_id: 1, condition: COND_OK,
}
const ITEM_2 = {
  id: 2, inventory_no: 'INV-0002', description: null,
  tool_id: 2, tool: TOOL_BOHR,
  status_id: 2, status: STATUS_LOANED,
  condition_id: 2, condition: COND_WORN,
}

const USER_ADMIN   = { id: 1, firstname: 'Anna', lastname: 'Admin',   email: 'admin@firma.de',   is_active: true, role_id: 1, department_id: 1, role: { id: 1, name: 'ADMIN' },              department: { id: 1, name: 'Fertigung' }, created_at: '2026-01-01T00:00:00', updated_at: '2026-01-01T00:00:00' }
const USER_MANAGER = { id: 2, firstname: 'Max',  lastname: 'Manager', email: 'manager@firma.de', is_active: true, role_id: 2, department_id: 1, role: { id: 2, name: 'DEPARTMENT_MANAGER' }, department: { id: 1, name: 'Fertigung' }, created_at: '2026-01-01T00:00:00', updated_at: '2026-01-01T00:00:00' }
const USER_EMP     = { id: 3, firstname: 'Eva',  lastname: 'Emp',     email: 'emp@firma.de',     is_active: true, role_id: 3, department_id: 2, role: { id: 3, name: 'EMPLOYEE' },           department: { id: 2, name: 'Lager' },     created_at: '2026-01-01T00:00:00', updated_at: '2026-01-01T00:00:00' }

const SLIM_ADMIN = { id: 1, firstname: 'Anna', lastname: 'Admin',   email: 'admin@firma.de' }
const SLIM_EMP   = { id: 3, firstname: 'Eva',  lastname: 'Emp',     email: 'emp@firma.de' }

export const MOCK = {
  roles: [
    { id: 1, name: 'ADMIN' },
    { id: 2, name: 'DEPARTMENT_MANAGER' },
    { id: 3, name: 'EMPLOYEE' },
  ],
  departments: [
    { id: 1, name: 'Fertigung', lead_user_id: 2 },
    { id: 2, name: 'Lager',     lead_user_id: null },
  ],
  users: [USER_ADMIN, USER_MANAGER, USER_EMP],
  categories: [CATEGORY_HW, CATEGORY_EL],
  toolStatuses: [
    STATUS_AVAIL,
    STATUS_LOANED,
    { id: 3, name: 'DEFECT' },
    { id: 4, name: 'MAINTENANCE' },
    { id: 5, name: 'RETIRED' },
  ],
  toolConditions: [
    COND_OK,
    COND_WORN,
    { id: 3, name: 'DEFECT' },
  ],
  issueStatuses: [
    { id: 1, name: 'OPEN' },
    { id: 2, name: 'IN_PROGRESS' },
    { id: 3, name: 'RESOLVED' },
    { id: 4, name: 'CLOSED' },
  ],
  loanRequestStatuses: [
    { id: 1, name: 'REQUESTED' },
    { id: 2, name: 'APPROVED' },
    { id: 3, name: 'REJECTED' },
    { id: 4, name: 'CANCELLED' },
  ],
  tools: [TOOL_HAMMER, TOOL_BOHR],
  toolItems: [ITEM_1, ITEM_2],
  issues: [
    {
      id: 1,
      tool_item_id: 1,
      tool_item: ITEM_1,
      reported_by_user_id: 3,
      reported_by: SLIM_EMP,
      status_id: 1,
      status: { id: 1, name: 'OPEN' },
      title: 'Griff gebrochen',
      description: 'Der Griff ist gerissen',
      reported_at: '2026-03-10T10:00:00',
      resolved_at: null,
    },
  ],
  loanRequests: [
    {
      id: 1,
      requester_user_id: 3,
      requester: SLIM_EMP,
      approver_user_id: null,
      approver: null,
      request_status_id: 1,
      status: { id: 1, name: 'REQUESTED' },
      due_at: null,
      days_needed: 3,
      requested_at: '2026-03-15T09:00:00',
      decision_at: null,
      decision_comment: null,
      comment: 'Für Regalaufbau',
      items: [{ id: 1, request_id: 1, tool_id: 1, tool: TOOL_HAMMER, quantity: 1 }],
    },
  ],
  loans: [
    {
      id: 1,
      issued_at: '2026-03-15T09:00:00',
      due_at: '2026-03-22T09:00:00',
      returned_at: null,
      borrower_user_id: 3,
      borrower: SLIM_EMP,
      issued_by_user_id: 1,
      issuer: SLIM_ADMIN,
      returned_by_user_id: null,
      return_processor: null,
      comment: null,
      items: [{
        id: 1, loan_id: 1, tool_item_id: 1, tool_item: ITEM_1,
        return_condition_id: null, return_condition: null, return_comment: null,
      }],
      is_overdue: false,
    },
  ],
}

/** Register all common API mocks for a page. Call before page.goto(). */
export async function mockAllApis(page: Page) {
  await page.route('**/auth/login',              r => json(r, { access_token: TOKENS.admin, token_type: 'bearer' }))
  await page.route('**/auth/logout',             r => json(r, {}))
  await page.route('**/api/v1/getusers',         r => json(r, MOCK.users))
  await page.route('**/api/v1/getuser/**',       r => json(r, MOCK.users[0]))
  await page.route('**/api/v1/createuser',       r => json(r, MOCK.users[0], 201))
  await page.route('**/api/v1/updateuser/**',    r => json(r, MOCK.users[0]))
  await page.route('**/api/v1/deleteuser/**',    r => json(r, {}, 204))
  await page.route('**/api/v1/getdepartments',   r => json(r, MOCK.departments))
  await page.route('**/api/v1/getdepartment/**', r => json(r, MOCK.departments[0]))
  await page.route('**/api/v1/createdepartment', r => json(r, MOCK.departments[0], 201))
  await page.route('**/api/v1/updatedepartment/**', r => json(r, MOCK.departments[0]))
  await page.route('**/api/v1/deletedepartment/**', r => json(r, {}, 204))
  await page.route('**/api/v1/getroles',         r => json(r, MOCK.roles))
  await page.route('**/api/v1/gettoolcategories',r => json(r, MOCK.categories))
  await page.route('**/api/v1/gettoolstatuses',  r => json(r, MOCK.toolStatuses))
  await page.route('**/api/v1/gettoolconditions',r => json(r, MOCK.toolConditions))
  await page.route('**/api/v1/gettoolitemissuestatuses', r => json(r, MOCK.issueStatuses))
  await page.route('**/api/v1/getloanrequeststatuses',   r => json(r, MOCK.loanRequestStatuses))
  await page.route('**/api/v1/gettools',         r => json(r, MOCK.tools))
  await page.route('**/api/v1/gettool/**',       r => json(r, MOCK.tools[0]))
  await page.route('**/api/v1/createtool',       r => json(r, MOCK.tools[0], 201))
  await page.route('**/api/v1/updatetool/**',    r => json(r, MOCK.tools[0]))
  await page.route('**/api/v1/deletetool/**',    r => json(r, {}, 204))
  await page.route('**/api/v1/gettoolitems',     r => json(r, MOCK.toolItems))
  await page.route('**/api/v1/gettoolitem/**',   r => json(r, MOCK.toolItems[0]))
  await page.route('**/api/v1/createtoolitem',   r => json(r, MOCK.toolItems[0], 201))
  await page.route('**/api/v1/updatetoolitem/**',r => json(r, MOCK.toolItems[0]))
  await page.route('**/api/v1/retiretoolitm/**', r => json(r, { ...MOCK.toolItems[0], status: { id: 5, name: 'Ausgemustert' } }))
  await page.route('**/api/v1/deletetoolitem/**',r => json(r, {}, 204))
  await page.route('**/api/v1/gettoolitemhistory/**', r => json(r, []))
  await page.route('**/api/v1/gettoolitemqrcode/**',  r => r.fulfill({ status: 200, contentType: 'image/png', body: Buffer.alloc(0) }))
  await page.route('**/api/v1/gettoolitemissues',         r => json(r, MOCK.issues))
  await page.route('**/api/v1/gettoolitemissue/**',        r => json(r, MOCK.issues[0]))
  await page.route('**/api/v1/createtoolitemissue',        r => json(r, MOCK.issues[0], 201))
  await page.route('**/api/v1/updatetoolitemissue/**',     r => json(r, MOCK.issues[0]))
  await page.route('**/api/v1/deletetoolitemissue/**',     r => json(r, {}, 204))
  await page.route('**/api/v1/getloanrequests',            r => json(r, MOCK.loanRequests))
  await page.route('**/api/v1/getloanrequest/**',          r => json(r, MOCK.loanRequests[0]))
  await page.route('**/api/v1/createloanrequest',          r => json(r, MOCK.loanRequests[0], 201))
  await page.route('**/api/v1/updateloanrequest/**',       r => json(r, MOCK.loanRequests[0]))
  await page.route('**/api/v1/decideloanrequest/**',       r => json(r, { ...MOCK.loanRequests[0], status: { id: 2, name: 'APPROVED' } }))
  await page.route('**/api/v1/deleteloanrequest/**',       r => json(r, {}, 204))
  await page.route('**/api/v1/getloans',                   r => json(r, MOCK.loans))
  await page.route('**/api/v1/getoverdueloans',            r => json(r, []))
  await page.route('**/api/v1/getloan/**',                 r => json(r, MOCK.loans[0]))
  await page.route('**/api/v1/createloan',                 r => json(r, MOCK.loans[0], 201))
  await page.route('**/api/v1/returnloan/**',              r => json(r, { ...MOCK.loans[0], returned_at: '2026-03-20T12:00:00' }))
  await page.route('**/api/v1/deleteloan/**',              r => json(r, {}, 204))
}
