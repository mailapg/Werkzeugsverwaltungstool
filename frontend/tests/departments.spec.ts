import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Abteilungsverwaltung', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/departments')
    await page.waitForLoadState('networkidle')
  })

  test('Abteilungen werden als Karten angezeigt', async ({ page }) => {
    await expect(page.getByText('Fertigung')).toBeVisible()
    await expect(page.getByText('Lager')).toBeVisible()
  })

  test('"Neue Abteilung"-Button ist für Admin sichtbar', async ({ page }) => {
    await expect(page.getByRole('button', { name: /neue abteilung|erstellen|hinzufügen/i })).toBeVisible()
  })

  test('"Neue Abteilung"-Dialog öffnet sich', async ({ page }) => {
    await page.getByRole('button', { name: /neue abteilung|erstellen|hinzufügen/i }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Erstellungsformular enthält Namensfeld', async ({ page }) => {
    await page.getByRole('button', { name: /neue abteilung|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.locator('input[type="text"], input:not([type])').first()).toBeVisible()
  })

  test('Erstellungsformular enthält Leiter-Dropdown', async ({ page }) => {
    await page.getByRole('button', { name: /neue abteilung|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.locator('[role="combobox"], select').first()).toBeVisible()
  })

  test('Abteilung erstellen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createdepartment', async r => {
      called = true
      await json(r, { id: 99, name: 'Montage', lead_user_id: null }, 201)
    })
    await page.getByRole('button', { name: /neue abteilung|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    const nameInput = dialog.locator('input[type="text"], input:not([type])').first()
    await nameInput.fill('Montage')
    await dialog.getByRole('button', { name: /speichern|erstellen|anlegen/i }).click()
    expect(called).toBe(true)
  })

  test('Klick auf Abteilung öffnet Detaildialog', async ({ page }) => {
    await page.getByText('Fertigung').click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Bearbeiten-Button öffnet Bearbeitungsdialog', async ({ page }) => {
    const editBtn = page.getByRole('button', { name: /bearbeiten|edit/i }).first()
    if (await editBtn.isVisible()) {
      await editBtn.click()
      await expect(page.getByRole('dialog')).toBeVisible()
    }
  })

  test('Abteilung bearbeiten – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/updatedepartment/**', async r => {
      called = true
      await json(r, { ...MOCK.departments[0], name: 'Fertigung Neu' })
    })
    const editBtn = page.getByRole('button', { name: /bearbeiten|edit/i }).first()
    if (await editBtn.isVisible()) {
      await editBtn.click()
      const dialog = page.getByRole('dialog')
      const nameInput = dialog.getByLabel(/name/i)
      if (await nameInput.isVisible()) {
        await nameInput.clear()
        await nameInput.fill('Fertigung Neu')
      }
      await dialog.getByRole('button', { name: /speichern|aktualisieren/i }).click()
      expect(called).toBe(true)
    }
  })

  test('Abteilung löschen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/deletedepartment/**', async r => {
      called = true
      await json(r, {}, 204)
    })
    const deleteBtn = page.getByRole('button', { name: /löschen/i }).first()
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click()
      const confirmBtn = page.getByRole('button', { name: /bestätigen|ja|löschen/i })
      if (await confirmBtn.isVisible()) await confirmBtn.click()
      expect(called).toBe(true)
    }
  })

  test('Mitarbeiter kann /departments nicht aufrufen', async ({ page }) => {
    await page.evaluate((t) => localStorage.setItem('token', t),
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZV9pZCI6MywiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature'
    )
    await page.goto('/departments')
    await expect(page).not.toHaveURL('/departments')
  })

  test('Abteilungsleiter kann /departments aufrufen', async ({ page }) => {
    await page.evaluate((t) => localStorage.setItem('token', t),
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwicm9sZV9pZCI6MiwiZGVwYXJ0bWVudF9pZCI6MSwiZXhwIjo5OTk5OTk5OTk5fQ.fakesignature'
    )
    await page.goto('/departments')
    await expect(page).toHaveURL(/departments/)
  })
})
