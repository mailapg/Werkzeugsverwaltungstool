import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { jwtDecode } from 'jwt-decode'
import { authApi } from '../api/services'
import type { AuthUser } from '../types'

const ADMIN_ID = 1
const MANAGER_ID = 2

interface JwtPayload {
  sub: string
  role_id: number
  department_id: number
}

interface AuthContextType {
  user: AuthUser | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isAdmin: boolean
  isManager: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

function decodeUser(token: string): AuthUser | null {
  try {
    const payload = jwtDecode<JwtPayload>(token)
    return { id: Number(payload.sub), role_id: payload.role_id, department_id: payload.department_id }
  } catch { return null }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [user, setUser] = useState<AuthUser | null>(() => {
    const t = localStorage.getItem('token')
    return t ? decodeUser(t) : null
  })

  useEffect(() => {
    setUser(token ? decodeUser(token) : null)
  }, [token])

  const login = async (email: string, password: string) => {
    const data = await authApi.login(email, password)
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    setUser(decodeUser(data.access_token))
  }

  const logout = async () => {
    try { await authApi.logout() } catch { /* ignore */ }
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      logout,
      isAdmin: user?.role_id === ADMIN_ID,
      isManager: user?.role_id === MANAGER_ID || user?.role_id === ADMIN_ID,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
