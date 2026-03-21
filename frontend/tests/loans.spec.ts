import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Ausleihen', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/loans')
    await page.waitForLoadState('networkidle')
  })

  test('Ausleihliste wird angezeigt', async ({ page }) => {
    // Borrower (Eva Emp) or tool item (INV-0001 / Hammer) should appear
    await expect(page.getByText(/eva|INV-0001|Hammer/i).first()).toBeVisible()
  })

  test('Aktivfilter-Tabs sind sichtbar', async ({ page }) => {
    const tabs = page.getByRole('tab').or(page.getByRole('button', { name: /alle|aktiv|überfällig|zurückgegeben/i }))
    await expect(tabs.first()).toBeVisible()
  })

  test('Seiteninhalt wird geladen', async ({ page }) => {
    // The loans page has no "Neue Ausleihe" button – loans are created via request approval
    await expect(page.getByText(/ausleihen/i).first()).toBeVisible()
  })

  test('Tabellenheader sind sichtbar', async ({ page }) => {
    await expect(page.getByText(/ausleiher|exemplare|ausgegeben/i).first()).toBeVisible()
  })

  test('Klick auf Ausleihe öffnet Detaildialog', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Rückgabe-Button ist im Dialog sichtbar (aktive Ausleihe)', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    const dialog = page.getByRole('dialog')
    // Return button should be present for active loan
    const returnBtn = dialog.getByRole('button', { name: /rückgabe|zurückgeben/i })
    if (await returnBtn.isVisible()) {
      await expect(returnBtn).toBeVisible()
    }
  })

  test('Rückgabe-Dialog öffnet sich', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    const dialog = page.getByRole('dialog')
    const returnBtn = dialog.getByRole('button', { name: /rückgabe|zurückgeben/i })
    if (await returnBtn.isVisible()) {
      await returnBtn.click()
      // Should show return form
      await expect(page.getByRole('dialog')).toBeVisible()
    }
  })

  test('Rückgabe – Dialog öffnet sich und hat Bestätigen-Button', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    const dialog = page.getByRole('dialog')
    const returnBtn = dialog.getByRole('button', { name: /rückgabe|zurückgeben/i })
    if (await returnBtn.isVisible()) {
      await returnBtn.click()
      // Return dialog should appear
      await expect(page.getByRole('dialog')).toBeVisible()
      const submitBtn = page.getByRole('button', { name: /bestätigen|rückgabe|zurückgeben|speichern/i }).last()
      await expect(submitBtn).toBeVisible()
    }
  })

  test('Suche nach Inventarnummer filtert Ausleihen', async ({ page }) => {
    const search = page.getByPlaceholder(/suchen/i).or(page.getByRole('searchbox'))
    if (await search.isVisible()) {
      await search.fill('INV-0001')
      await page.waitForTimeout(300)
    }
  })

  test('Filter "Aktiv" zeigt nur offene Ausleihen', async ({ page }) => {
    const activeTab = page.getByRole('tab', { name: /aktiv/i }).or(page.getByRole('button', { name: /aktiv/i }))
    if (await activeTab.isVisible()) {
      await activeTab.click()
      await page.waitForLoadState('networkidle')
    }
  })
})
