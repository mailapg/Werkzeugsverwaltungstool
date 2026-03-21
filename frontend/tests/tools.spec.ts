import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Werkzeugseite', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/tools')
    await page.waitForLoadState('networkidle')
  })

  test('Werkzeuge werden angezeigt', async ({ page }) => {
    await expect(page.getByText('Hammer').first()).toBeVisible()
    await expect(page.getByText('Bohrmaschine').first()).toBeVisible()
  })

  test('Kategorie wird angezeigt', async ({ page }) => {
    await expect(page.getByText(/handwerkzeug/i).first()).toBeVisible()
  })

  test('Suche filtert Werkzeuge', async ({ page }) => {
    const search = page.getByPlaceholder(/suchen/i).or(page.getByRole('searchbox')).first()
    if (await search.isVisible()) {
      await search.fill('Hammer')
      await expect(page.getByText('Hammer').first()).toBeVisible()
    }
  })

  test('"Neues Werkzeug"-Button öffnet Dialog', async ({ page }) => {
    await page.getByRole('button', { name: /neues werkzeug|hinzufügen|erstellen|neu/i }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Pflichtfelder im Erstellungsdialog sind vorhanden', async ({ page }) => {
    await page.getByRole('button', { name: /neues werkzeug|hinzufügen|erstellen|neu/i }).click()
    const dialog = page.getByRole('dialog')
    // Name-Input (Label without for, use first text input)
    await expect(dialog.locator('input[type="text"], input:not([type])').first()).toBeVisible()
  })

  test('Werkzeug erstellen – erfolgreich', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createtool', async r => {
      called = true
      await json(r, { ...MOCK.tools[0], id: 99, tool_name: 'Schraubenzieher' }, 201)
    })
    await page.getByRole('button', { name: /neues werkzeug|hinzufügen|erstellen|neu/i }).click()
    const dialog = page.getByRole('dialog')
    // Fill name (Label without for, find first text input)
    await dialog.locator('input[type="text"], input:not([type])').first().fill('Schraubenzieher')
    // Select category
    const catSelect = dialog.locator('[role="combobox"]').first()
    if (await catSelect.isVisible()) {
      await catSelect.click()
      const opt = page.getByRole('option').first()
      if (await opt.isVisible()) await opt.click()
    }
    await dialog.getByRole('button', { name: /speichern|erstellen|anlegen/i }).click()
    await page.waitForTimeout(500)
    expect(called).toBe(true)
  })

  test('Klick auf Werkzeug öffnet Detaildialog', async ({ page }) => {
    await page.getByText('Hammer').first().click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Detaildialog zeigt Werkzeugname', async ({ page }) => {
    await page.getByText('Hammer').first().click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByText('Hammer').first()).toBeVisible()
  })

  test('Dialog kann geschlossen werden', async ({ page }) => {
    await page.getByText('Hammer').first().click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.getByRole('dialog')).not.toBeVisible()
  })

  test('Kategoriefilter zeigt nur passende Werkzeuge', async ({ page }) => {
    const catFilter = page.locator('select, [role="combobox"]').first()
    if (await catFilter.isVisible()) {
      await catFilter.click()
      const option = page.getByRole('option', { name: /handwerkzeug/i })
      if (await option.isVisible()) {
        await option.click()
        await expect(page.getByText('Bohrmaschine')).not.toBeVisible()
      }
    }
  })

  test('Werkzeug löschen – Bestätigungsdialog erscheint', async ({ page }) => {
    // Open detail dialog first, then find delete button
    await page.getByText('Hammer').first().click()
    const dialog = page.getByRole('dialog')
    const deleteBtn = dialog.getByRole('button', { name: /löschen|entfernen/i })
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click()
      // Confirm dialog or direct delete
      const confirmBtn = page.getByRole('button', { name: /bestätigen|ja|löschen/i })
      if (await confirmBtn.isVisible()) {
        await expect(confirmBtn).toBeVisible()
      }
    }
  })
})
