// ============================================================
// AuthContext.tsx – Globaler Authentifizierungszustand
//
// React Context stellt Login-Informationen für alle Komponenten bereit,
// ohne Props durch viele Ebenen weitergeben zu müssen.
//
// Bereitgestellt:
//   - user: { id, role_id, department_id } aus dem JWT
//   - token: der JWT-String
//   - login() / logout()
//   - isAdmin: true wenn role_id === 1
//   - isManager: true wenn role_id === 1 oder 2
// ============================================================

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { jwtDecode } from 'jwt-decode'
import { authApi } from '../api/services'
import type { AuthUser } from '../types'

// Rollen-IDs müssen mit den Backend-Konstanten übereinstimmen (role_ids.py)
const ADMIN_ID = 1
const MANAGER_ID = 2

// TypeScript-Typ für den JWT-Payload (was im Token steckt)
interface JwtPayload {
  sub: string          // Benutzer-ID als String (Standard-Claim)
  role_id: number      // Rolle des Benutzers
  department_id: number // Abteilung des Benutzers
}

// TypeScript-Interface: Was der Context nach außen bereitstellt
interface AuthContextType {
  user: AuthUser | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isAdmin: boolean
  isManager: boolean
}

// Context-Objekt erstellen (initial null, wird durch Provider gefüllt)
const AuthContext = createContext<AuthContextType | null>(null)

/**
 * Liest und dekodiert den JWT-Token aus einem String.
 * Gibt null zurück wenn der Token ungültig ist (z.B. abgelaufen oder korrupt).
 */
function decodeUser(token: string): AuthUser | null {
  try {
    const payload = jwtDecode<JwtPayload>(token)
    return { id: Number(payload.sub), role_id: payload.role_id, department_id: payload.department_id }
  } catch { return null }
}

/**
 * AuthProvider – umschließt die gesamte App in App.tsx.
 * Verwaltet den Login-Zustand und stellt ihn über den Context bereit.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  // Token aus localStorage lesen (bleibt nach Seitenneuladen erhalten)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  // Benutzerinfos direkt beim Start aus dem gespeicherten Token dekodieren
  const [user, setUser] = useState<AuthUser | null>(() => {
    const t = localStorage.getItem('token')
    return t ? decodeUser(t) : null
  })

  // Wenn sich das Token ändert, Benutzerinfos aktualisieren
  useEffect(() => {
    setUser(token ? decodeUser(token) : null)
  }, [token])

  /**
   * Login: Sendet Credentials an das Backend, speichert das Token.
   * Throws wenn Login fehlschlägt (falsche Credentials).
   */
  const login = async (email: string, password: string) => {
    const data = await authApi.login(email, password)
    localStorage.setItem('token', data.access_token)  // Token persistent speichern
    setToken(data.access_token)
    setUser(decodeUser(data.access_token))
  }

  /**
   * Logout: Token beim Backend sperren (Blacklist) und lokal löschen.
   * Fehler beim API-Aufruf werden ignoriert (Token wird trotzdem lokal gelöscht).
   */
  const logout = async () => {
    try { await authApi.logout() } catch { /* ignorieren – lokaler Logout trotzdem */ }
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
      // isManager gilt auch für Admins, damit Admins alle Manager-Funktionen nutzen können
      isManager: user?.role_id === MANAGER_ID || user?.role_id === ADMIN_ID,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * useAuth – Custom Hook zum Zugriff auf den Auth-Context.
 * Muss innerhalb von <AuthProvider> verwendet werden.
 *
 * Beispiel:
 *   const { user, isAdmin, logout } = useAuth()
 */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
