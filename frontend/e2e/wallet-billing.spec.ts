/**
 * Wallet and billing E2E tests.
 * Covers: wallet balance, billing tabs, payment requests, receipts.
 */
import { test, expect } from "@playwright/test";
import { login } from "./helpers/auth";

async function getToken(page: import("@playwright/test").Page, email: string, pass: string) {
  return page.evaluate(
    async ({ email, password }) => {
      const r = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      return (await r.json()).access_token as string;
    },
    { email, password: pass },
  );
}

test.describe("Client — wallet and billing UI", () => {
  test.beforeEach(async ({ page }) => login(page, "client"));

  test("billing & wallet page loads via /client/money", async ({ page }) => {
    await page.goto("/client/money");
    await expect(page.getByRole("heading", { name: /billing.*wallet|wallet.*billing/i })).toBeVisible();
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("wallet tab shows balance", async ({ page }) => {
    await page.goto("/client/money");
    await page.getByRole("button", { name: /wallet/i }).click();
    // Balance should display (even if 0)
    await expect(page.getByText(/balance|available/i)).toBeVisible({ timeout: 5_000 });
  });

  test("invoices tab loads without error", async ({ page }) => {
    await page.goto("/client/money");
    await page.getByRole("button", { name: /invoices/i }).click();
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("payment requests tab loads without error", async ({ page }) => {
    await page.goto("/client/money");
    await page.getByRole("button", { name: /invoices.*receipts|receipts/i }).first().click().catch(() => {});
    // Try payment requests tab
    const prTab = page.getByRole("button", { name: /payment.?request/i });
    if (await prTab.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await prTab.click();
      await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
    } else {
      test.skip();
    }
  });

  test("receipts tab loads without error", async ({ page }) => {
    await page.goto("/client/money");
    const receiptsTab = page.getByRole("button", { name: /receipt/i });
    if (await receiptsTab.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await receiptsTab.click();
      await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
    } else {
      test.skip();
    }
  });

  test("dashboard wallet card links to /client/money", async ({ page }) => {
    await page.goto("/client");
    const walletCard = page.locator("a[href='/client/money']").first();
    await expect(walletCard).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("API — wallet endpoints", () => {
  test("wallet balance endpoint responds", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");
    const wallet = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/wallets/me/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status, data: await r.json() };
      },
      { token },
    );
    expect([200]).toContain(wallet.status);
    expect(wallet.data?.available_balance ?? wallet.data?.balance).toBeDefined();
  });

  test("wallet entries list is accessible", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");
    const entries = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/wallets/me/entries/?limit=5", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(entries.status);
  });

  test("admin wallet view is accessible", async ({ page }) => {
    const token = await getToken(page, "admin@test.local", "admin1234");
    const wallets = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/wallets/admin/wallets/?limit=10", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(wallets.status);
  });

  test("client invoices are accessible", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");
    const invoices = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/billing/my/invoices/?limit=5", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(invoices.status);
  });

  test("client receipts are accessible", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");
    const receipts = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/billing/my/receipts/?limit=5", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(receipts.status);
  });
});
