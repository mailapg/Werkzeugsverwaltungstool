// ============================================================
// api/client.ts – Zentraler Axios HTTP-Client
//
// Axios ist eine Bibliothek für HTTP-Anfragen (besser als natives fetch).
// Hier wird die globale Konfiguration für alle API-Aufrufe gesetzt:
//   1. Base-URL: Alle Anfragen gehen automatisch an das Backend
//   2. Request-Interceptor: JWT-Token automatisch zu jeder Anfrage hinzufügen
//   3. Response-Interceptor: Bei 401 automatisch zur Login-Seite weiterleiten
// ============================================================

import axios from 'axios'

// Axios-Instanz mit der Backend-Basis-URL erstellen.
// VITE_API_URL kann in .env gesetzt werden, Standard ist http://localhost:8000
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

// Request-Interceptor: Wird vor JEDER ausgehenden Anfrage ausgeführt.
// Fügt automatisch den JWT-Token als Authorization-Header hinzu,
// damit man das nicht in jeder einzelnen API-Funktion machen muss.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`  // "Bearer <token>"
  }
  return config
})

// Response-Interceptor: Wird bei JEDER Serverantwort ausgeführt.
// Wenn das Backend 401 Unauthorized zurückgibt (Token abgelaufen/gesperrt),
// wird der Benutzer automatisch zur Login-Seite weitergeleitet.
api.interceptors.response.use(
  (res) => res,  // Erfolgreiche Antworten einfach durchreichen
  (err) => {
    if (err.response?.status === 401 && window.location.pathname !== '/login') {
      // Token ungültig – lokal aufräumen und zur Login-Seite weiterleiten
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)  // Fehler weiterwerfen für Fehlerbehandlung in Komponenten
  }
)

export default api
