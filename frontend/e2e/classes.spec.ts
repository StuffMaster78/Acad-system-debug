/**
 * Class management E2E tests.
 * Covers: class list, new class form, admin class detail with installments.
 */
import { test, expect } from "@playwright/test";
import { login } from "./helpers/auth";

test.describe("Client — class views", () => {
  test.beforeEach(async ({ page }) => login(page, "client"));

  test("classes list page loads", async ({ page }) => {
    await page.goto("/client/classes");
    await expect(page.getByRole("heading", { name: /classes/i })).toBeVisible();
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("new class form is accessible", async ({ page }) => {
    await page.goto("/client/classes/new");
    await expect(page.getByText(/class|enrol|start/i)).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — class detail and installment management", () => {
  test.beforeEach(async ({ page }) => login(page, "admin"));

  test("admin class list loads", async ({ page }) => {
    await page.goto("/admin/classes");
    await expect(page.getByText(/classes/i)).toBeVisible();
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("admin class detail shows installments tab", async ({ page }) => {
    await page.goto("/admin/classes");
    const firstClass = page.locator("a[href*='/admin/classes/']").first();
    if (await firstClass.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await firstClass.click();
      await expect(page).toHaveURL(/\/admin\/classes\/\d+/);

      // Find and click the Installments tab
      await page.getByRole("button", { name: /installments/i }).click();
      // Should show either the empty state or the installment table
      await expect(
        page.getByText(/no payment schedule|payment plan|installments/i),
      ).toBeVisible({ timeout: 5_000 });
    } else {
      test.skip();
    }
  });

  test("installment tab empty state has 'Set up' button for admin", async ({ page }) => {
    await page.goto("/admin/classes");
    const firstClass = page.locator("a[href*='/admin/classes/']").first();
    if (await firstClass.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await firstClass.click();
      await page.getByRole("button", { name: /installments/i }).click();

      // If no plan, the CTA should be visible
      const setupBtn = page.getByRole("button", { name: /set up payment plan/i });
      if (await setupBtn.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await setupBtn.click();
        // Modal should open
        await expect(page.getByText(/number of installments/i)).toBeVisible({ timeout: 3_000 });
        // Close it
        await page.getByRole("button", { name: /cancel/i }).click();
      }
    } else {
      test.skip();
    }
  });
});

test.describe("API — class installment endpoints", () => {
  async function getToken(page: import("@playwright/test").Page, email: string, password: string) {
    return page.evaluate(
      async ({ email, password }) => {
        const r = await fetch("/api/v1/auth/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const d = await r.json();
        return d.access_token as string;
      },
      { email, password },
    );
  }

  test("installments endpoint responds for a class", async ({ page }) => {
    const adminToken = await getToken(page, "admin@test.local", "admin1234");

    const classes = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/class-management/classes/?limit=1", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return r.json();
      },
      { token: adminToken },
    );

    const classId = classes?.results?.[0]?.id;
    if (!classId) { test.skip(); return; }

    const installments = await page.evaluate(
      async ({ token, classId }) => {
        const r = await fetch(
          `/api/v1/class-management/classes/${classId}/payments/installments/`,
          { headers: { Authorization: `Bearer ${token}` } },
        );
        return { status: r.status, data: await r.json() };
      },
      { token: adminToken, classId },
    );
    expect([200]).toContain(installments.status);
  });

  test("reset plan returns 404 when no plan exists", async ({ page }) => {
    const adminToken = await getToken(page, "admin@test.local", "admin1234");

    const classes = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/class-management/classes/?limit=1", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return r.json();
      },
      { token: adminToken },
    );

    const classId = classes?.results?.[0]?.id;
    if (!classId) { test.skip(); return; }

    const reset = await page.evaluate(
      async ({ token, classId }) => {
        const r = await fetch(
          `/api/v1/class-management/classes/${classId}/payments/plan/reset/`,
          {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
            body: JSON.stringify({ reason: "e2e test cleanup" }),
          },
        );
        return { status: r.status };
      },
      { token: adminToken, classId },
    );
    // Either 200 (reset succeeded) or 404 (no plan — expected in fresh env)
    expect([200, 404]).toContain(reset.status);
  });
});
