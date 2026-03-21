import { test, expect } from '@playwright/test'
import { json, TOKENS } from './helpers'

test.describe('Authentifizierung', () => {

  test('Login-Seite wird angezeigt', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: /anmelden|werkzeug|login/i })).toBeVisible()
    await expect(page.getByLabel(/e-mail/i)).toBeVisible()
    await expect(page.getByLabel(/passwort/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /anmelden|login/i })).toBeVisible()
  })

  test('Ohne Token wird auf /login weitergeleitet', async ({ page }) => {
    await page.goto('/login')
    await page.evaluate(() => localStorage.removeItem('token'))
    await page.goto('/')
    await expect(page).toHaveURL(/login/)
  })

  test('Erfolgreicher Login leitet zum Dashboard weiter', async ({ page }) => {
    await page.route('**/auth/login', r =>
      json(r, { access_token: TOKENS.admin, token_type: 'bearer' })
    )
    await page.route('**/api/v1/**', r => json(r, []))

    await page.goto('/login')
    await page.getByLabel(/e-mail/i).fill('admin@firma.de')
    await page.getByLabel(/passwort/i).fill('admin123')
    await page.getByRole('button', { name: /anmelden|login/i }).click()
    await expect(page).toHaveURL('/')
  })

  test('Falsche Zugangsdaten zeigen Fehlermeldung', async ({ page }) => {
    await page.route('**/auth/login', r =>
      r.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Ungültige Anmeldedaten' }) })
    )
    await page.goto('/login')
    await page.getByLabel(/e-mail/i).fill('falsch@firma.de')
    await page.getByLabel(/passwort/i).fill('falsch')
    await page.getByRole('button', { name: /anmelden|login/i }).click()
    // Error should appear (toast or inline)
    await expect(page.getByText(/ungültig|fehler|falsch|error/i)).toBeVisible({ timeout: 5000 })
  })

  test('Leere Felder verhindern Absenden', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: /anmelden|login/i }).click()
    // Still on login page
    await expect(page).toHaveURL(/login/)
  })

  test('Logout löscht Token und leitet zu /login', async ({ page }) => {
    await page.route('**/auth/logout', r => json(r, {}))
    await page.route('**/api/v1/**', r => json(r, []))
    await page.goto('/login')
    await page.evaluate((t) => localStorage.setItem('token', t), TOKENS.admin)
    await page.goto('/')
    await page.getByRole('button', { name: /abmelden|logout/i }).click()
    await expect(page).toHaveURL(/login/)
    const token = await page.evaluate(() => localStorage.getItem('token'))
    expect(token).toBeNull()
  })

  test('Mitarbeiter-Token gewährt Zugang zum Dashboard', async ({ page }) => {
    await page.route('**/api/v1/**', r => json(r, []))
    await page.goto('/login')
    await page.evaluate((t) => localStorage.setItem('token', t), TOKENS.employee)
    await page.goto('/')
    await expect(page).not.toHaveURL(/login/)
  })

  test('Admin-Only-Route /users ist für Mitarbeiter gesperrt', async ({ page }) => {
    await page.route('**/api/v1/**', r => json(r, []))
    await page.goto('/login')
    await page.evaluate((t) => localStorage.setItem('token', t), TOKENS.employee)
    await page.goto('/users')
    // Should redirect away from /users
    await expect(page).not.toHaveURL(/\/users$/)
  })
})
