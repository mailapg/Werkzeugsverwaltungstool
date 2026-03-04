import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toolsApi, toolItemsApi, loansApi, loanRequestsApi, usersApi, issuesApi } from '../api/services'
import type { Tool, ToolItem, Loan, LoanRequest, User, ToolItemIssue } from '../types'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Skeleton } from '../components/ui/skeleton'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { Wrench, Package, ArrowLeftRight, ClipboardList, AlertTriangle, Users } from 'lucide-react'
import { toolStatusLabel, issueStatusLabel, loanRequestStatusLabel, t } from '../lib/labels'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function StatCard({ title, value, icon: Icon, color, to }: { title: string; value: number; icon: React.ElementType; color: string; to: string }) {
  const navigate = useNavigate()
  return (
    <Card className="border-0 shadow-md cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all" onClick={() => navigate(to)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500 font-medium">{title}</p>
            <p className="text-3xl font-bold text-slate-800 mt-1">{value}</p>
          </div>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
            <Icon size={22} className="text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { isAdmin, isManager } = useAuth()
  const navigate = useNavigate()
  const [tools, setTools] = useState<Tool[]>([])
  const [items, setItems] = useState<ToolItem[]>([])
  const [loans, setLoans] = useState<Loan[]>([])
  const [requests, setRequests] = useState<LoanRequest[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [issues, setIssues] = useState<ToolItemIssue[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      toolsApi.list(),
      toolItemsApi.list(),
      loansApi.list(),
      loanRequestsApi.list(),
      isAdmin ? usersApi.list() : Promise.resolve([]),
      isAdmin ? issuesApi.list() : Promise.resolve([]),
    ]).then(([t, i, l, r, u, iss]) => {
      setTools(t); setItems(i); setLoans(l)
      setRequests(r); setUsers(u as User[]); setIssues(iss)
    }).finally(() => setLoading(false))
  }, [isAdmin])

  // Chart data
  const statusData = ['AVAILABLE', 'LOANED', 'DEFECT', 'MAINTENANCE', 'RETIRED'].map(s => ({
    name: t(toolStatusLabel, s),
    value: items.filter(i => i.status.name === s).length,
  })).filter(d => d.value > 0)

  const categoryData = tools.reduce<Record<string, number>>((acc, t) => {
    acc[t.category.name] = (acc[t.category.name] || 0) + 1
    return acc
  }, {})
  const catChartData = Object.entries(categoryData).map(([name, value]) => ({ name, value }))

  const issueStatusData = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'].map(s => ({
    key: s,
    name: t(issueStatusLabel, s),
    value: issues.filter(i => i.status.name === s).length,
  })).filter(d => d.value > 0)

  const activeLoans = loans.filter(l => !l.returned_at).length
  const overdueLoans = loans.filter(l => l.is_overdue).length
  const openRequests = requests.filter(r => r.status.name === 'REQUESTED').length

  if (loading) return (
    <div className="p-8 space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28" />)}
      </div>
    </div>
  )

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 mt-1">Übersicht über das Werkzeugverwaltungssystem</p>
      </div>

      {/* Stats */}
      <div className={cn('grid grid-cols-2 gap-4', isAdmin ? 'lg:grid-cols-3 xl:grid-cols-5' : 'lg:grid-cols-2 xl:grid-cols-4')}>
        <StatCard title="Werkzeugtypen"   value={tools.length}   icon={Wrench}        color="bg-blue-500"    to="/tools" />
        <StatCard title="Exemplare"        value={items.length}   icon={Package}       color="bg-indigo-500"  to="/inventory" />
        <StatCard title="Aktive Ausleihen" value={activeLoans}    icon={ArrowLeftRight} color="bg-emerald-500" to="/loans?filter=active" />
        <StatCard title="Offene Anfragen"  value={openRequests}   icon={ClipboardList} color="bg-amber-500"   to="/loan-requests?filter=REQUESTED" />
        {isAdmin && <StatCard title="Nutzer" value={users.length} icon={Users}         color="bg-purple-500"  to="/users" />}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/inventory')}>
          <CardHeader>
            <CardTitle className="text-slate-700 text-base">Exemplare nach Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={statusData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%" cy="50%"
                  outerRadius={85}
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  labelLine={false}
                  style={{ cursor: 'pointer' }}
                >
                  {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/tools')}>
          <CardHeader>
            <CardTitle className="text-slate-700 text-base">Werkzeuge nach Kategorie</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={Math.max(240, catChartData.length * 28)}>
              <BarChart data={catChartData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
                <Tooltip />
                <Bar dataKey="value" name="Anzahl" fill="#3b82f6" radius={[0, 4, 4, 0]} style={{ cursor: 'pointer' }} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isAdmin && <Card className="border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/issues')}>
          <CardHeader>
            <CardTitle className="text-slate-700 text-base">Issues nach Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={issueStatusData} margin={{ left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" name="Anzahl" radius={[4, 4, 0, 0]} style={{ cursor: 'pointer' }}>
                  {issueStatusData.map((entry, i) => (
                    <Cell key={i} fill={entry.key === 'OPEN' ? '#ef4444' : entry.key === 'IN_PROGRESS' ? '#f59e0b' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>}

        <Card className={cn('border-0 shadow-md cursor-pointer hover:shadow-lg transition-shadow', !isAdmin && 'lg:col-span-2')} onClick={() => navigate('/loan-requests')}>
          <CardHeader>
            <CardTitle className="text-slate-700 text-base">Anfragen-Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 pt-2">
              {['REQUESTED', 'APPROVED', 'REJECTED', 'CANCELLED'].map(status => {
                const count = requests.filter(r => r.status.name === status).length
                const total = requests.length || 1
                const pct = Math.round((count / total) * 100)
                const colors: Record<string, string> = { REQUESTED: 'bg-amber-500', APPROVED: 'bg-emerald-500', REJECTED: 'bg-red-500', CANCELLED: 'bg-slate-400' }
                return (
                  <div key={status}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-600">{t(loanRequestStatusLabel, status)}</span>
                      <span className="font-semibold text-slate-700">{count}</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${colors[status]}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent overdue */}
      {(isAdmin || isManager) && overdueLoans > 0 && (
        <Card className="border-0 shadow-md border-l-4 border-l-red-500 cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/loans')}>
          <CardHeader>
            <CardTitle className="text-red-600 text-base flex items-center gap-2">
              <AlertTriangle size={18} /> {overdueLoans} überfällige Ausleihe{overdueLoans !== 1 ? 'n' : ''}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {loans.filter(l => l.is_overdue).slice(0, 5).map(loan => (
                <div key={loan.id} className="flex items-center justify-between text-sm py-1 border-b border-slate-100 last:border-0">
                  <span className="text-slate-700">#{loan.id} – {loan.borrower.firstname} {loan.borrower.lastname}</span>
                  <Badge variant="destructive">{new Date(loan.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
