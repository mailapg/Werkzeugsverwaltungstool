import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK } from './helpers'

test.describe('Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/')
  })

  test('Dashboard lädt ohne Fehler', async ({ page }) => {
    await expect(page).not.toHaveURL(/login/)
    // Wait for content to appear
    await page.waitForLoadState('networkidle')
  })

  test('Sidebar-Navigation ist sichtbar', async ({ page }) => {
    await expect(page.getByRole('navigation').or(page.locator('aside')).first()).toBeVisible()
  })

  test('Dashboard-Seite enthält KPI-Karten', async ({ page }) => {
    // At least one statistic card should be visible
    await expect(page.locator('[class*="card"], [class*="Card"]').first()).toBeVisible()
  })

  test('Admin sieht Nutzerverwaltung in der Sidebar', async ({ page }) => {
    await expect(page.getByRole('link', { name: /nutzer/i })).toBeVisible()
  })

  test('Admin sieht Rollenverwaltung in der Sidebar', async ({ page }) => {
    await expect(page.getByRole('link', { name: /rollen/i })).toBeVisible()
  })

  test('Navigation zu Werkzeugseite funktioniert', async ({ page }) => {
    await page.getByRole('link', { name: /werkzeug/i }).first().click()
    await expect(page).toHaveURL(/tools/)
  })

  test('Navigation zu Inventarseite funktioniert', async ({ page }) => {
    await page.getByRole('link', { name: /inventar/i }).click()
    await expect(page).toHaveURL(/inventory/)
  })

  test('Navigation zu Ausleihen funktioniert', async ({ page }) => {
    await page.getByRole('link', { name: /ausleihen/i }).click()
    await expect(page).toHaveURL(/loans/)
  })

  test('Navigation zu Anfragen funktioniert', async ({ page }) => {
    await page.getByRole('link', { name: /anfragen/i }).click()
    await expect(page).toHaveURL(/loan-requests/)
  })

  test('Navigation zu Meldungen funktioniert', async ({ page }) => {
    await page.getByRole('link', { name: /meldungen/i }).click()
    await expect(page).toHaveURL(/issues/)
  })

  test('Mitarbeiter sieht keine Admin-Links', async ({ page }) => {
    await page.evaluate((t) => localStorage.setItem('token', t),
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZV9pZCI6MywiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature'
    )
    await page.goto('/')
    await expect(page.getByRole('link', { name: /^nutzer$/i })).not.toBeVisible()
    await expect(page.getByRole('link', { name: /^rollen$/i })).not.toBeVisible()
  })
})
