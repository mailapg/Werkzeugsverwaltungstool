import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'

interface Props {
  children?: ReactNode
  requireAdmin?: boolean
  requireManager?: boolean
}

export default function ProtectedRoute({ children, requireAdmin, requireManager }: Props) {
  const { user, isAdmin, isManager } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (requireAdmin && !isAdmin) return <Navigate to="/" replace />
  if (requireManager && !isManager) return <Navigate to="/" replace />
  return children ? <>{children}</> : <Outlet />
}
