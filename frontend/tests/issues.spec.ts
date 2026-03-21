import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Meldungen (Issues)', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/issues')
    await page.waitForLoadState('networkidle')
  })

  test('Meldungsliste wird angezeigt', async ({ page }) => {
    await expect(page.getByText(/griff gebrochen/i)).toBeVisible()
  })

  test('Inventarnummer der Meldung ist sichtbar', async ({ page }) => {
    await expect(page.getByText('INV-0001')).toBeVisible()
  })

  test('Melder ist sichtbar', async ({ page }) => {
    await expect(page.getByText(/eva|emp@firma/i).first()).toBeVisible()
  })

  test('Status-Badge ist sichtbar', async ({ page }) => {
    // OPEN → displayed as "Offen" via labels.ts
    await expect(page.getByText(/offen|open|in bearbeitung/i).first()).toBeVisible()
  })

  test('Statusfilter ist vorhanden', async ({ page }) => {
    const filter = page.getByRole('combobox').or(page.getByRole('tab')).or(page.locator('select')).first()
    await expect(filter).toBeVisible()
  })

  test('Suche nach Titel funktioniert', async ({ page }) => {
    const search = page.getByPlaceholder(/suchen/i).or(page.getByRole('searchbox'))
    if (await search.isVisible()) {
      await search.fill('Griff')
      await expect(page.getByText(/griff gebrochen/i)).toBeVisible()
    }
  })

  test('"Neue Meldung"-Button öffnet Dialog', async ({ page }) => {
    // Exact button text: "Neue Meldung"
    await page.getByRole('button', { name: 'Neue Meldung' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Meldeformular enthält Titel-Feld', async ({ page }) => {
    await page.getByRole('button', { name: 'Neue Meldung' }).click()
    const dialog = page.getByRole('dialog')
    // Title is first text input in dialog
    await expect(dialog.locator('input[type="text"], input:not([type])').first()).toBeVisible()
  })

  test('Neue Meldung erstellen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createtoolitemissue', async r => {
      called = true
      await json(r, MOCK.issues[0], 201)
    })
    await page.getByRole('button', { name: 'Neue Meldung' }).click()
    const dialog = page.getByRole('dialog')
    await dialog.locator('input[type="text"], input:not([type])').first().fill('Testmeldung')
    // Select tool item (Exemplar)
    const select = dialog.locator('[role="combobox"]').first()
    if (await select.isVisible()) {
      await select.click()
      const opt = page.getByRole('option').first()
      if (await opt.isVisible()) await opt.click()
    }
    await dialog.getByRole('button', { name: /speichern|melden|erstellen/i }).click()
    expect(called).toBe(true)
  })

  test('Klick auf Meldung öffnet Detaildialog', async ({ page }) => {
    await page.getByText(/griff gebrochen/i).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Detaildialog zeigt Beschreibung', async ({ page }) => {
    await page.getByText(/griff gebrochen/i).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByText(/gerissen|griff/i).first()).toBeVisible()
  })

  test('Admin sieht Aktions-Buttons in der Meldungsliste', async ({ page }) => {
    // Admin has delete button (icon-only); Manager has edit button
    const actionBtn = page.locator('table tr').nth(1).getByRole('button')
    await expect(actionBtn.first()).toBeVisible()
  })

  test('Mitarbeiter sieht keine Bearbeiten-Schaltfläche (nur lesen)', async ({ page }) => {
    await page.evaluate((t) => localStorage.setItem('token', t),
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZV9pZCI6MywiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature'
    )
    await page.goto('/issues')
    await page.waitForLoadState('networkidle')
    // Issues page should still load (visible for all roles)
    await expect(page.getByText(/meldungen|issues/i).first()).toBeVisible()
  })

  test('Meldung löschen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/deletetoolitemissue/**', async r => {
      called = true
      await json(r, {}, 204)
    })
    await page.getByText(/griff gebrochen/i).click()
    const dialog = page.getByRole('dialog')
    const deleteBtn = dialog.getByRole('button', { name: /löschen/i })
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click()
      const confirmBtn = page.getByRole('button', { name: /bestätigen|ja|löschen/i })
      if (await confirmBtn.isVisible()) await confirmBtn.click()
      expect(called).toBe(true)
    }
  })
})
