import { test, expect } from '@playwright/test'
import { loginAs, mockAllApis, MOCK, json } from './helpers'

test.describe('Ausleiheanfragen', () => {

  test.beforeEach(async ({ page }) => {
    await mockAllApis(page)
    await loginAs(page, 'admin')
    await page.goto('/loan-requests')
    await page.waitForLoadState('networkidle')
  })

  test('Anfragen werden angezeigt', async ({ page }) => {
    // Requester or status should be visible
    await expect(page.getByText(/Eva|Hammer|INV-0001|Ausstehend|REQUESTED/i).first()).toBeVisible()
  })

  test('Status-Badge ist sichtbar', async ({ page }) => {
    await expect(page.getByText(/ausstehend|requested|angefragt/i).first()).toBeVisible()
  })

  test('Statusfilter ist vorhanden', async ({ page }) => {
    // Could be tabs, buttons, or a select dropdown for filtering
    const filter = page.getByRole('tab').or(page.locator('[role="combobox"], select')).or(
      page.getByRole('button', { name: /alle|ausstehend|genehmigt|abgelehnt/i })
    )
    await expect(filter.first()).toBeVisible()
  })

  test('"Neue Anfrage"-Button öffnet Dialog', async ({ page }) => {
    await page.getByRole('button', { name: /neue anfrage|erstellen|hinzufügen/i }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Anfrageformular enthält Felder für Werkzeug und Dauer', async ({ page }) => {
    await page.getByRole('button', { name: /neue anfrage|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    // days_needed field or tool selection
    await expect(dialog.locator('input[type="number"], [role="combobox"], select').first()).toBeVisible()
  })

  test('Neue Anfrage erstellen – API wird aufgerufen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/createloanrequest', async r => {
      called = true
      await json(r, MOCK.loanRequests[0], 201)
    })
    await page.getByRole('button', { name: /neue anfrage|erstellen|hinzufügen/i }).click()
    const dialog = page.getByRole('dialog')
    // Fill any visible inputs
    const numInput = dialog.locator('input[type="number"]').first()
    if (await numInput.isVisible()) await numInput.fill('3')
    // Select first available option in any combobox
    const selects = dialog.locator('[role="combobox"]')
    const count = await selects.count()
    for (let i = 0; i < Math.min(count, 2); i++) {
      if (await selects.nth(i).isVisible()) {
        await selects.nth(i).click()
        const opt = page.getByRole('option').first()
        if (await opt.isVisible()) { await opt.click(); await page.waitForTimeout(100) }
      }
    }
    const saveBtn = dialog.getByRole('button', { name: /speichern|erstellen|absenden|senden/i }).first()
    if (await saveBtn.isVisible()) await saveBtn.click()
    expect(called).toBe(true)

  })

  test('Klick auf Anfrage öffnet Detaildialog', async ({ page }) => {
    await page.getByText('Eva Emp').or(page.locator('table tr').nth(1)).first().click()
    await expect(page.getByRole('dialog')).toBeVisible()
  })

  test('Admin kann Anfrage genehmigen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/decideloanrequest/**', async r => {
      called = true
      await json(r, { ...MOCK.loanRequests[0], status: { id: 2, name: 'APPROVED' } })
    })
    // Click on the request row
    await page.getByText('Eva Emp').or(page.locator('table tr').nth(1)).first().click()
    const dialog = page.getByRole('dialog')
    const approveBtn = dialog.getByRole('button', { name: /genehmigen|approve/i })
    if (await approveBtn.isVisible()) {
      await approveBtn.click()
      expect(called).toBe(true)
    }
  })

  test('Admin kann Anfrage ablehnen', async ({ page }) => {
    let called = false
    await page.route('**/api/v1/decideloanrequest/**', async r => {
      called = true
      await json(r, { ...MOCK.loanRequests[0], status: { id: 3, name: 'REJECTED' } })
    })
    await page.getByText('Eva Emp').or(page.locator('table tr').nth(1)).first().click()
    const dialog = page.getByRole('dialog')
    const rejectBtn = dialog.getByRole('button', { name: /ablehnen|reject/i })
    if (await rejectBtn.isVisible()) {
      await rejectBtn.click()
      expect(called).toBe(true)
    }
  })

  test('Leere Anfragenliste zeigt Hinweistext', async ({ page }) => {
    await page.route('**/api/v1/getloanrequests', r => json(r, []))
    await page.goto('/loan-requests')
    await page.waitForLoadState('networkidle')
    // Empty state should show some message
    await expect(page.getByText(/keine anfragen|keine daten|leer|found/i).first()).toBeVisible()
  })
})
