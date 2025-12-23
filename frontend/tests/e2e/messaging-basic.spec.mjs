// Basic high-value E2E checks for messaging flows.
// Assumptions:
// - You can log in as an admin user at /login.
// - After login you land on a dashboard where you can navigate to an order detail
//   that already has seeded threads/messages.
// - These selectors/routes may need minor tweaks to match your actual UI.

import { test, expect } from '@playwright/test'

test.describe('Messaging basics', () => {
  test('admin can open an order thread and see messages', async ({ page }) => {
    // LOGIN
    await page.goto('/login')
    await page.fill('input[name="email"]', process.env.E2E_ADMIN_EMAIL || 'admin@example.com')
    await page.fill('input[name="password"]', process.env.E2E_ADMIN_PASSWORD || 'password')
    await page.click('button[type="submit"]')

    // Wait for dashboard
    await page.waitForURL('**/admin/**', { timeout: 20000 })

    // Navigate to an order detail (adjust selector as needed)
    await page.click('a[data-test="orders-link"]')
    await page.waitForURL('**/orders**')

    // Click first order row
    await page.click('[data-test="order-row"]:first-child')
    await page.waitForURL('**/orders/**')

    // Open Messages tab (or equivalent)
    await page.click('[data-test="order-tab-messages"]')

    // Expect threads list to be visible
    await expect(page.locator('[data-test="order-threads-list"]')).toBeVisible()

    // Open first thread
    await page.click('[data-test="order-thread-item"]:first-child')

    // Thread modal should appear and messages should be visible
    await expect(page.locator('[data-test="thread-view-modal"]')).toBeVisible()
    await expect(page.locator('.message-bubble')).toHaveCountGreaterThan(0)
  })
})


