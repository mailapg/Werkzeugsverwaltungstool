// ============================================================
// App.tsx – Haupt-Einstiegspunkt der React-Anwendung
//
// Hier wird das gesamte Routing der App definiert.
// React Router DOM steuert, welche Seite bei welcher URL angezeigt wird.
//
// Schutzebenen:
//   1. Öffentlich: /login (kein Token nötig)
//   2. Eingeloggt: Alle anderen Seiten (Token nötig)
//   3. Manager/Admin: /departments
//   4. Nur Admin: /users, /roles
// ============================================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsersPage from './pages/UsersPage'
import DepartmentsPage from './pages/DepartmentsPage'
import ToolsPage from './pages/ToolsPage'
import InventoryPage from './pages/InventoryPage'
import IssuesPage from './pages/IssuesPage'
import LoanRequestsPage from './pages/LoanRequestsPage'
import LoansPage from './pages/LoansPage'
import ToolItemDetailPage from './pages/ToolItemDetailPage'
import RolesPage from './pages/RolesPage'
import { Toaster } from './components/ui/sonner'

export default function App() {
  return (
    // AuthProvider stellt den Login-Status für die gesamte App bereit (React Context)
    <AuthProvider>
      {/* BrowserRouter ermöglicht clientseitiges Routing (URL ändert sich ohne Seitenneuladen) */}
      <BrowserRouter>
        <Routes>
          {/* Öffentliche Route: Login-Seite ist ohne Authentifizierung erreichbar */}
          <Route path="/login" element={<LoginPage />} />

          {/* Alle folgenden Seiten benötigen einen gültigen JWT-Token */}
          <Route element={<ProtectedRoute />}>
            {/* AppLayout enthält Sidebar und Navigation – alle Seiten werden darin eingebettet */}
            <Route element={<AppLayout />}>
              {/* Für alle eingeloggten Benutzer zugänglich */}
              <Route path="/" element={<DashboardPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/inventory/detail" element={<ToolItemDetailPage />} />
              <Route path="/loan-requests" element={<LoanRequestsPage />} />
              <Route path="/loans" element={<LoansPage />} />
              <Route path="/issues" element={<IssuesPage />} />

              {/* Nur für Manager und Admins – requireManager prüft role_id */}
              <Route element={<ProtectedRoute requireManager />}>
                <Route path="/departments" element={<DepartmentsPage />} />
              </Route>

              {/* Nur für Admins – requireAdmin prüft ob role_id === 1 */}
              <Route element={<ProtectedRoute requireAdmin />}>
                <Route path="/users" element={<UsersPage />} />
                <Route path="/roles" element={<RolesPage />} />
              </Route>
            </Route>
          </Route>

          {/* Fallback: Unbekannte URLs leiten zur Startseite weiter */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Toaster zeigt globale Benachrichtigungen (Erfolg/Fehler) oben rechts an */}
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  )
}
