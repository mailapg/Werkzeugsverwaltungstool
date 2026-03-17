import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Building2, Wrench, Package,
  AlertTriangle, ClipboardList, ArrowLeftRight, Shield, LogOut, ChevronRight,
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { cn } from '../../lib/utils'
import { roleLabel, t } from '../../lib/labels'

const ADMIN_ID = 1
const MANAGER_ID = 2
const EMPLOYEE_ID = 3

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/tools', icon: Wrench, label: 'Werkzeuge', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/inventory', icon: Package, label: 'Inventar', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/loan-requests', icon: ClipboardList, label: 'Ausleiheanfragen', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/loans', icon: ArrowLeftRight, label: 'Ausleihen', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/issues', icon: AlertTriangle, label: 'Meldungen', roles: [ADMIN_ID, MANAGER_ID, EMPLOYEE_ID] },
  { to: '/departments', icon: Building2, label: 'Abteilungen', roles: [ADMIN_ID, MANAGER_ID] },
  { to: '/users', icon: Users, label: 'Nutzer', roles: [ADMIN_ID] },
  { to: '/roles', icon: Shield, label: 'Rollen', roles: [ADMIN_ID] },
]

export default function Sidebar() {
  const { user, logout, isAdmin, isManager } = useAuth()

  const visible = navItems.filter(item => user && item.roles.includes(user.role_id))

  return (
    <aside className="flex flex-col w-64 h-screen sticky top-0 bg-slate-900 text-slate-100 overflow-hidden">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-700">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center">
          <Wrench size={18} className="text-white" />
        </div>
        <div>
          <p className="font-semibold text-sm leading-tight">Werkzeugverwaltung</p>
        </div>
      </div>

      {/* Role badge */}
      <div className="px-4 py-3 border-b border-slate-700">
        <span className={cn(
          'text-xs font-medium px-2 py-1 rounded-full',
          isAdmin && 'bg-red-500/20 text-red-300',
          !isAdmin && isManager && 'bg-amber-500/20 text-amber-300',
          !isManager && 'bg-emerald-500/20 text-emerald-300',
        )}>
          {isAdmin ? t(roleLabel, 'ADMIN') : isManager ? t(roleLabel, 'DEPARTMENT_MANAGER') : t(roleLabel, 'EMPLOYEE')}
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {visible.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => cn(
              'flex items-center gap-3 mx-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all mb-0.5',
              isActive
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/40'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100',
            )}
          >
            <Icon size={17} />
            <span className="flex-1">{label}</span>
            <ChevronRight size={14} className="opacity-40" />
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-slate-700">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-all"
        >
          <LogOut size={17} />
          Abmelden
        </button>
      </div>
    </aside>
  )
}
