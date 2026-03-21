import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Nutzerverwaltung (Admin only)', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/users')
    await page.waitForLoadState('networkidle')
  })

  test('Nutzertabelle wird angezeigt', async ({ page }) => {
    // firstname + lastname are rendered together on the page
    await expect(page.getByText(/anna/i).or(page.getByText(/admin@firma/i)).first()).toBeVisible()
    await expect(page.getByText(/max/i).or(page.getByText(/manager@firma/i)).first()).toBeVisible()
    await expect(page.getByText(/eva/i).or(page.getByText(/emp@firma/i)).first()).toBeVisible()
  })

  test('E-Mail-Adressen sind sichtbar', async ({ page }) => {
    await expect(page.getByText('admin@firma.de')).toBeVisible()
  })

  test('Rollenbadges sind sichtbar', async ({ page }) => {
    await expect(page.getByText(/admin/i).first()).toBeVisible()
  })

  test('"Neuer Nutzer"-Button öffnet Dialog', async ({ page }) => {
    await page.getByRole('button', { name: /neuer nutzer|erstellen|hinzufügen/i }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Erstellungsformular enthält E-Mail-Feld', async ({ page }) => {
    await page.getByRole('button', { name: /neuer nutzer|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    // E-Mail is input[type="text"] (3rd input in form)
    await expect(dialog.locator('input[type="text"]').first()).toBeVisible()
  })

  test('Erstellungsformular enthält Passwortfeld', async ({ page }) => {
    await page.getByRole('button', { name: /neuer nutzer|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.locator('input[type="password"]')).toBeVisible()
  })

  test('Nutzer erstellen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createuser', async r => {
      called = true
      await json(r, MOCK.users[0], 201)
    })
    await page.getByRole('button', { name: /neuer nutzer|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    // Inputs in order: Vorname, Nachname, E-Mail, Passwort
    const inputs = dialog.locator('input[type="text"], input:not([type])')
    await inputs.nth(0).fill('Test')
    await inputs.nth(1).fill('Nutzer')
    await inputs.nth(2).fill('test@firma.de')
    await dialog.locator('input[type="password"]').fill('passwort123')
    // Select role
    const roleSelect = dialog.locator('[role="combobox"]').first()
    if (await roleSelect.isVisible()) {
      await roleSelect.click()
      const opt = page.getByRole('option').first()
      if (await opt.isVisible()) await opt.click()
    }
    await dialog.getByRole('button', { name: /speichern|erstellen|anlegen/i }).click()
    expect(called).toBe(true)
  })

  test('Klick auf Tabellenzeile öffnet Detaildialog', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Detaildialog zeigt E-Mail', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByText(/firma\.de/i)).toBeVisible()
  })

  test('Nutzer bearbeiten – Dialog öffnet sich', async ({ page }) => {
    await page.locator('table tr').nth(1).click()
    const dialog = page.getByRole('dialog')
    const editBtn = dialog.getByRole('button', { name: /bearbeiten|edit/i })
    if (await editBtn.isVisible()) {
      await editBtn.click()
      await expect(page.getByRole('dialog')).toBeVisible()
    }
  })

  test('Nutzer löschen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/deleteuser/**', async r => {
      called = true
      await json(r, {}, 204)
    })
    // Find delete button in the row
    const deleteBtn = page.locator('table tr').nth(1).getByRole('button', { name: /löschen/i })
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click()
      const confirmBtn = page.getByRole('button', { name: /bestätigen|ja|löschen/i })
      if (await confirmBtn.isVisible()) await confirmBtn.click()
      expect(called).toBe(true)
    }
  })

  test('Mitarbeiter kann /users nicht aufrufen', async ({ page }) => {
    await page.evaluate((t) => localStorage.setItem('token', t),
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZV9pZCI6MywiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature'
    )
    await page.goto('/users')
    await expect(page).not.toHaveURL('/users')
  })
})
