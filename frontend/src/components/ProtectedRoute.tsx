// ============================================================
// ProtectedRoute.tsx – Routenschutz nach Authentifizierung und Rolle
//
// Schützt Seiten vor unberechtigtem Zugriff.
// Verwendung in App.tsx:
//   <Route element={<ProtectedRoute />}> → nur eingeloggte Benutzer
//   <Route element={<ProtectedRoute requireAdmin />}> → nur Admins
//   <Route element={<ProtectedRoute requireManager />}> → Manager + Admins
// ============================================================

import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'

interface Props {
  children?: ReactNode
  requireAdmin?: boolean    // Wenn true: nur Admins (role_id === 1)
  requireManager?: boolean  // Wenn true: Admins und Manager (role_id === 1 oder 2)
}

export default function ProtectedRoute({ children, requireAdmin, requireManager }: Props) {
  const { user, isAdmin, isManager } = useAuth()

  // Nicht eingeloggt → zur Login-Seite weiterleiten
  if (!user) return <Navigate to="/login" replace />

  // Eingeloggt aber falsche Rolle → zur Startseite weiterleiten
  if (requireAdmin && !isAdmin) return <Navigate to="/" replace />
  if (requireManager && !isManager) return <Navigate to="/" replace />

  // Outlet rendert die untergeordneten Routen (wenn kein children prop übergeben wurde)
  return children ? <>{children}</> : <Outlet />
}
