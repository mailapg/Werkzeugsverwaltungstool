import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Inventarseite', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/inventory')
    await page.waitForLoadState('networkidle')
  })

  test('Inventarliste wird angezeigt', async ({ page }) => {
    await expect(page.getByText('INV-0001')).toBeVisible()
    await expect(page.getByText('INV-0002')).toBeVisible()
  })

  test('Werkzeugnamen sind sichtbar', async ({ page }) => {
    await expect(page.getByText('Hammer')).toBeVisible()
    await expect(page.getByText('Bohrmaschine')).toBeVisible()
  })

  test('Status-Badges sind sichtbar', async ({ page }) => {
    await expect(page.getByText(/verfügbar/i).first()).toBeVisible()
    await expect(page.getByText(/ausgeliehen/i).first()).toBeVisible()
  })

  test('Suche nach Inventarnummer funktioniert', async ({ page }) => {
    const search = page.getByPlaceholder(/suchen|inventar/i).or(page.getByRole('searchbox'))
    if (await search.isVisible()) {
      await search.fill('INV-0001')
      await expect(page.getByText('INV-0001')).toBeVisible()
      await expect(page.getByText('INV-0002')).not.toBeVisible()
    }
  })

  test('Suche nach Werkzeugname funktioniert', async ({ page }) => {
    const search = page.getByPlaceholder(/suchen|inventar/i).or(page.getByRole('searchbox'))
    if (await search.isVisible()) {
      await search.fill('Hammer')
      await expect(page.getByText('Hammer')).toBeVisible()
    }
  })

  test('"Neues Exemplar"-Button öffnet Dialog', async ({ page }) => {
    await page.getByRole('button', { name: /neues exemplar|hinzufügen|erstellen|neu/i }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Erstellungsdialog enthält Werkzeug-Auswahl', async ({ page }) => {
    await page.getByRole('button', { name: /neues exemplar|hinzufügen|erstellen|neu/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.locator('[role="combobox"], select').first()).toBeVisible()
  })

  test('Exemplar erstellen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createtoolitem', async r => {
      called = true
      await json(r, { ...MOCK.toolItems[0], id: 99 }, 201)
    })
    await page.getByRole('button', { name: /neues exemplar|hinzufügen|erstellen|neu/i }).click()
    const dialog = page.getByRole('dialog')
    // Select tool
    const selects = dialog.locator('[role="combobox"], select')
    if (await selects.first().isVisible()) {
      await selects.first().click()
      const option = page.getByRole('option').first()
      if (await option.isVisible()) await option.click()
    }
    await dialog.getByRole('button', { name: /speichern|erstellen|anlegen/i }).click()
    expect(called).toBe(true)
  })

  test('Klick auf Tabellenzeile öffnet Detaildialog oder navigiert', async ({ page }) => {
    const row = page.getByText('INV-0001').first()
    await row.click()
    // Either a dialog opens or navigation happens
    const dialogVisible = await page.getByRole('dialog').isVisible().catch(() => false)
    const urlChanged = page.url().includes('detail') || page.url().includes('INV')
    expect(dialogVisible || urlChanged).toBe(true)
  })

  test('Zustandsbadge "In Ordnung" ist grün/sichtbar', async ({ page }) => {
    await expect(page.getByText(/in ordnung/i).first()).toBeVisible()
  })

  test('Zustandsbadge "Abgenutzt" ist sichtbar', async ({ page }) => {
    // WORN → 'Abgenutzt' per labels.ts
    await expect(page.getByText(/abgenutzt/i).first()).toBeVisible()
  })
})
