/**
 * Admin and superadmin portal E2E tests.
 * Covers: all major admin views, financial center, ops intelligence, command center.
 */
import { test, expect } from "@playwright/test";
import { login } from "./helpers/auth";

// Module-level API helpers shared across all describe blocks
async function apiToken(page: import("@playwright/test").Page, email: string, pass: string) {
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

async function apiGetReq(page: import("@playwright/test").Page, tok: string, url: string) {
  return page.evaluate(
    async ({ tok, url }) => {
      const r = await fetch(url, { headers: { Authorization: `Bearer ${tok}` } });
      return { status: r.status, data: await r.json() };
    },
    { tok, url },
  );
}

test.describe("Admin portal — core views", () => {
  test.beforeEach(async ({ page }) => login(page, "admin"));

  test("admin dashboard loads", async ({ page }) => {
    await expect(page).toHaveURL(/\/admin/);
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("orders queue loads without error", async ({ page }) => {
    await page.goto("/admin/orders");
    await expect(page.getByText(/500|server error|unable to load/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("writers list loads", async ({ page }) => {
    await page.goto("/admin/writers");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("clients list loads", async ({ page }) => {
    await page.goto("/admin/clients");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("payments view loads", async ({ page }) => {
    await page.goto("/admin/payments");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("financial center loads", async ({ page }) => {
    await page.goto("/admin/financial");
    await expect(page.getByText(/500|server error|unable to load/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("operations command center loads correctly", async ({ page }) => {
    await page.goto("/admin/ops-command");
    await expect(page.getByText(/operations command center/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/unable to load the operations command center/i)).not.toBeVisible();
  });

  test("ops intelligence loads correctly", async ({ page }) => {
    await page.goto("/admin/ops");
    await expect(page.getByText(/ops intelligence/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/unable to load operations intelligence/i)).not.toBeVisible();
  });

  test("disputes view loads", async ({ page }) => {
    await page.goto("/admin/disputes");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("refunds view loads", async ({ page }) => {
    await page.goto("/admin/refunds");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("loyalty view loads", async ({ page }) => {
    await page.goto("/admin/loyalty");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("discounts view loads", async ({ page }) => {
    await page.goto("/admin/discounts");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("wallets admin view loads", async ({ page }) => {
    await page.goto("/admin/wallets");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("audit log view loads", async ({ page }) => {
    await page.goto("/admin/audit");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("analytics view loads", async ({ page }) => {
    await page.goto("/admin/analytics");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("config hub loads", async ({ page }) => {
    await page.goto("/admin/config");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("holidays view loads", async ({ page }) => {
    await page.goto("/admin/holidays");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("event system view loads (no 'failed to load events')", async ({ page }) => {
    await page.goto("/admin/events");
    await expect(page.getByText(/failed to load events/i)).not.toBeVisible({ timeout: 8_000 });
  });
});

test.describe("Superadmin portal — cross-tenant views", () => {
  test.beforeEach(async ({ page }) => login(page, "superadmin"));

  test("superadmin dashboard loads", async ({ page }) => {
    await expect(page).toHaveURL(/\/superadmin/);
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("tenants view loads", async ({ page }) => {
    await page.goto("/superadmin/tenants");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("appeals view loads", async ({ page }) => {
    await page.goto("/superadmin/appeals");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("finance view loads", async ({ page }) => {
    await page.goto("/superadmin/finance");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 8_000 });
  });
});

test.describe("API — admin critical endpoints", () => {
  async function token(page: import("@playwright/test").Page, email: string, pass: string) {
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

  async function get(page: import("@playwright/test").Page, tok: string, url: string) {
    return page.evaluate(
      async ({ tok, url }) => {
        const r = await fetch(url, { headers: { Authorization: `Bearer ${tok}` } });
        return { status: r.status };
      },
      { tok, url },
    );
  }

  test("operations command center returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/admin-management/operations-command-center/");
    expect(r.status).toBe(200);
  });

  test("orders ops summary returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/orders/ops/summary/");
    expect(r.status).toBe(200);
  });

  test("all ops queues return 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const queues = ["late", "critical", "awaiting_approval", "pending_staffing", "awaiting_acknowledgement"];
    for (const q of queues) {
      const r = await get(page, tok, `/api/v1/orders/ops/queues/${q}/`);
      expect(r.status).toBe(200);
    }
  });

  test("financial overview returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/admin-management/financial-overview/overview/");
    expect(r.status).toBe(200);
  });

  test("writers list returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/writer-management/writers/?limit=5");
    expect(r.status).toBe(200);
  });

  test("clients list returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/client-management/clients/?limit=5");
    expect(r.status).toBe(200);
  });

  test("loyalty tiers returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/loyalty-management/loyalty-tiers/");
    expect(r.status).toBe(200);
  });

  test("discounts endpoint returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/discounts/admin/discounts/?limit=5");
    expect(r.status).toBe(200);
  });

  test("event system list returns 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/events/");
    expect(r.status).toBe(200);
  });

  test("event metrics return 200", async ({ page }) => {
    const tok = await token(page, "admin@test.local", "admin1234");
    const r = await get(page, tok, "/api/v1/events/metrics/");
    expect(r.status).toBe(200);
  });
});

// ─── User management — new capabilities ──────────────────────────────────────

test.describe("Admin — user profile extended actions", () => {
  test.beforeEach(async ({ page }) => login(page, "admin"));

  test("user directory loads at /admin/access", async ({ page }) => {
    await page.goto("/admin/access");
    await expect(page.getByText(/user directory/i)).toBeVisible({ timeout: 8_000 });
  });

  test("user profile page shows impersonation section", async ({ page }) => {
    await page.goto("/admin/access");
    const viewBtn = page.locator("button", { hasText: "View profile" });
    await expect(viewBtn.first()).toBeVisible({ timeout: 8_000 });
    await viewBtn.first().click();
    await page.waitForURL(/\/admin\/users\/\d+/);
    await expect(page.getByText(/impersonation/i)).toBeVisible({ timeout: 6_000 });
  });

  test("user profile shows Support auth links section with magic link button", async ({ page }) => {
    await page.goto("/admin/access");
    await page.locator("button", { hasText: "View profile" }).first().click();
    await page.waitForURL(/\/admin\/users\/\d+/);
    await expect(page.getByText(/support auth links/i)).toBeVisible({ timeout: 6_000 });
    await expect(page.getByRole("button", { name: /generate magic link/i })).toBeVisible();
  });

  test("email edit button is present on user overview tab", async ({ page }) => {
    await page.goto("/admin/access");
    await page.locator("button", { hasText: "View profile" }).first().click();
    await page.waitForURL(/\/admin\/users\/\d+/);
    await expect(page.getByRole("button", { name: /^edit$/i })).toBeVisible({ timeout: 6_000 });
  });

  test("security-events endpoint returns 200", async ({ page }) => {
    const tok = await apiToken(page, "admin@test.local", "admin1234");
    const r = await apiGetReq(page, tok, "/api/v1/auth/security-events/");
    expect(r.status).toBe(200);
  });
});

// ─── MFA / security settings ──────────────────────────────────────────────────

test.describe("MFA & security settings", () => {
  test("TOTP setup endpoint returns device and QR code", async ({ page }) => {
    const tok = await apiToken(page, "client@test.local", "test1234");
    const r = await apiGetReq(page, tok, "/api/v1/auth/mfa/devices/"); // list first
    expect(r.status).toBe(200);

    const setup = await page.evaluate(
      async ({ tok }) => {
        const res = await fetch("/api/v1/auth/mfa/totp/setup/", {
          method: "POST",
          headers: { Authorization: `Bearer ${tok}`, "Content-Type": "application/json" },
          body: JSON.stringify({ name: "E2E Test App" }),
        });
        return { status: res.status, data: await res.json() };
      },
      { tok },
    );
    expect(setup.status).toBe(201);
    expect(setup.data).toHaveProperty("device_id");
    expect(setup.data).toHaveProperty("qr_code_base64");
    expect(typeof setup.data.secret).toBe("string");
  });

  test("client account page shows Two-factor authentication section", async ({ page }) => {
    await login(page, "client");
    await page.goto("/client/account");
    await expect(page.getByText(/two-factor authentication/i)).toBeVisible({ timeout: 8_000 });
    await expect(page.getByRole("button", { name: /add authenticator app/i })).toBeVisible();
  });

  test("client account page shows Security activity section", async ({ page }) => {
    await login(page, "client");
    await page.goto("/client/account");
    await expect(page.getByText(/security activity/i)).toBeVisible({ timeout: 8_000 });
  });

  test("session list endpoint returns active sessions for client", async ({ page }) => {
    const tok = await apiToken(page, "client@test.local", "test1234");
    const r = await apiGetReq(page, tok, "/api/v1/auth/sessions/");
    expect(r.status).toBe(200);
  });
});

// ─── Force-status order override ─────────────────────────────────────────────

test.describe("Force-status order endpoint", () => {
  test("admin can call force-status on an existing order", async ({ page }) => {
    const tok = await apiToken(page, "admin@test.local", "admin1234");
    const orders = await apiGetReq(page, tok, "/api/v1/orders/orders/?page_size=1");
    const ordersData = orders.data;
    const firstOrder = Array.isArray(ordersData)
      ? ordersData[0]
      : (ordersData?.results)?.[0];

    if (!firstOrder) {
      test.skip();
      return;
    }

    const result = await page.evaluate(
      async ({ tok, orderId, currentStatus }) => {
        const res = await fetch(`/api/v1/admin-management/orders/${orderId}/force-status/`, {
          method: "POST",
          headers: { Authorization: `Bearer ${tok}`, "Content-Type": "application/json" },
          body: JSON.stringify({ status: currentStatus, note: "E2E no-op force" }),
        });
        return { status: res.status };
      },
      { tok, orderId: firstOrder.id, currentStatus: firstOrder.status },
    );
    // 200 = success, 400 = validation issue — both are acceptable (not 403/404/500)
    expect([200, 400]).toContain(result.status);
  });
});
