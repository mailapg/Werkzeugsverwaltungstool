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
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/inventory/detail" element={<ToolItemDetailPage />} />
              <Route path="/loan-requests" element={<LoanRequestsPage />} />
              <Route path="/loans" element={<LoansPage />} />
              <Route path="/issues" element={<IssuesPage />} />

              {/* Manager + Admin */}
              <Route element={<ProtectedRoute requireManager />}>
                <Route path="/departments" element={<DepartmentsPage />} />
              </Route>

              {/* Admin only */}
              <Route element={<ProtectedRoute requireAdmin />}>
                <Route path="/users" element={<UsersPage />} />
                <Route path="/roles" element={<RolesPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  )
}
