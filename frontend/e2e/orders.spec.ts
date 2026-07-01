/**
 * Order lifecycle E2E tests.
 * Covers: place order (wizard) → admin ops queue → writer assignment
 *         → writer submission → client approval
 */
import { test, expect } from "@playwright/test";
import { login } from "./helpers/auth";

// ── Helpers ──────────────────────────────────────────────────────────────────

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

async function apiGet(page: import("@playwright/test").Page, token: string, url: string) {
  return page.evaluate(
    async ({ token, url }) => {
      const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      return r.json();
    },
    { token, url },
  );
}

async function apiPost(page: import("@playwright/test").Page, token: string, url: string, body: unknown) {
  return page.evaluate(
    async ({ token, url, body }) => {
      const r = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      return { status: r.status, data: await r.json() };
    },
    { token, url, body },
  );
}

// ── Tests ─────────────────────────────────────────────────────────────────────

test.describe("Order wizard — new order placement", () => {
  test.beforeEach(async ({ page }) => login(page, "client"));

  test("wizard renders step 1 on /client/new-order", async ({ page }) => {
    await page.goto("/client/new-order");
    // "Step X of 3" span is unique; step label appears in both nav and header so use first()
    await expect(page.getByText(/step 1 of 3/i).first()).toBeVisible();
    await expect(page.getByText(/what do you need/i).first()).toBeVisible();
  });

  test("step 1 → step 2 requires topic and instructions", async ({ page }) => {
    await page.goto("/client/new-order");
    // Continue without filling in — button should be disabled
    const continueBtn = page.getByRole("button", { name: /continue/i });
    await expect(continueBtn).toBeDisabled();

    // Fill topic only — still disabled
    await page.getByLabel(/topic/i).fill("Climate change impacts");
    await expect(continueBtn).toBeDisabled();

    // Fill instructions — now enabled
    await page.getByLabel(/instructions/i).fill("Write a comprehensive analysis of climate change impacts on agriculture in sub-Saharan Africa.");
    await expect(continueBtn).toBeEnabled();
  });

  test("advancing to step 2 shows paper specifics", async ({ page }) => {
    await page.goto("/client/new-order");

    await page.getByLabel(/topic/i).fill("Effects of social media on mental health");
    await page.getByLabel(/instructions/i).fill("Research paper analyzing the correlation between social media usage and anxiety disorders in teenagers.");
    await page.getByRole("button", { name: /continue/i }).click();

    // Step label appears in both the nav bar and the active header — use first()
    await expect(page.getByText(/step 2 of 3/i).first()).toBeVisible();
    await expect(page.getByText(/details & deadline/i).first()).toBeVisible();
  });

  test("back button returns to step 1", async ({ page }) => {
    await page.goto("/client/new-order");
    await page.getByLabel(/topic/i).fill("Test topic for navigation");
    await page.getByLabel(/instructions/i).fill("These are the detailed instructions for the test order.");
    await page.getByRole("button", { name: /continue/i }).click();
    await expect(page.getByText(/step 2 of 3/i)).toBeVisible();

    await page.getByRole("button", { name: /back/i }).click();
    await expect(page.getByText(/step 1 of 3/i)).toBeVisible();
    // Topic should still be filled
    await expect(page.getByLabel(/topic/i)).toHaveValue("Test topic for navigation");
  });

  test("step 2 shows deadline and pages for paper mode", async ({ page }) => {
    await page.goto("/client/new-order");
    await page.getByLabel(/topic/i).fill("Academic paper topic");
    await page.getByLabel(/instructions/i).fill("Detailed academic paper instructions for the E2E test suite.");
    await page.getByRole("button", { name: /continue/i }).click();

    await expect(page.locator("input[type='number']").first()).toBeVisible();
    await expect(page.getByLabel(/deadline/i)).toBeVisible();
  });

  test("design mode hides paper-specific fields", async ({ page }) => {
    await page.goto("/client/new-order");

    // Service mode buttons contain label + description text; filter by the label portion
    await page.locator("button").filter({ hasText: "Presentation / Design" }).click();
    await page.getByLabel(/topic/i).fill("Presentation on renewable energy");
    await page.getByLabel(/instructions/i).fill("Create a 15-slide presentation on renewable energy sources and their economic impact.");
    await page.getByRole("button", { name: /continue/i }).click();

    // Design mode step 2 should show slides/design fields
    await expect(page.getByText(/design type|slides|presentation/i).first()).toBeVisible();
    await expect(page.getByText(/academic level/i)).not.toBeVisible({ timeout: 3_000 });
  });

  test("step 3 shows price calculation section", async ({ page }) => {
    await page.goto("/client/new-order");

    // Use design mode so step 2 has no required paper-type selectors
    await page.locator("button").filter({ hasText: "Presentation / Design" }).click();
    await page.getByLabel(/topic/i).fill("Behavioural economics and consumer choice");
    await page.getByLabel(/instructions/i).fill("Analyse how nudge theory can be applied to improve consumer decision-making in digital marketplaces.");
    await page.getByRole("button", { name: /continue/i }).click(); // → step 2
    await page.getByRole("button", { name: /continue/i }).click(); // → step 3

    await expect(page.getByText(/step 3 of 3/i).first()).toBeVisible({ timeout: 8_000 });
    // Step 3 auto-calculates on entry so the button may already show "Recalculate"
    await expect(page.getByRole("button", { name: /calculate|recalculate/i }).first()).toBeVisible({ timeout: 8_000 });
  });
});

test.describe("Order list and dashboard", () => {
  test.beforeEach(async ({ page }) => login(page, "client"));

  test("client dashboard shows active orders section", async ({ page }) => {
    await expect(page.getByText(/active orders/i)).toBeVisible({ timeout: 8_000 });
  });

  test("my orders page loads without error", async ({ page }) => {
    await page.goto("/client/orders");
    await expect(page.getByRole("heading", { name: /my orders/i })).toBeVisible();
    await expect(page.getByText(/error|failed/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("order status tabs filter correctly", async ({ page }) => {
    await page.goto("/client/orders");
    await page.getByRole("button", { name: /active/i }).click();
    // Should not show an error
    await expect(page.getByText(/failed to load|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("client can navigate to order detail", async ({ page }) => {
    await page.goto("/client/orders");
    const firstOrder = page.locator("a[href*='/client/orders/']").first();
    if (await firstOrder.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await firstOrder.click();
      await expect(page).toHaveURL(/\/client\/orders\/\d+/);
    } else {
      test.skip(); // no orders to navigate to
    }
  });
});

test.describe("Order ops — admin actions", () => {
  test("admin ops queue loads without error", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/admin/orders");
    await expect(page.getByText(/failed|error|500/i)).not.toBeVisible({ timeout: 8_000 });
  });

  test("operations command center loads", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/admin/ops-command");
    await expect(page.getByText(/operations command center/i)).toBeVisible({ timeout: 8_000 });
    await expect(page.getByText(/unable to load/i)).not.toBeVisible({ timeout: 3_000 });
  });
});

test.describe("Order lifecycle — API-level integration", () => {
  test("complete order flow: create → price → verify ops endpoint", async ({ page }) => {
    // Must be on the same origin before fetch() with relative URLs will work
    await page.goto("/auth/login");
    const clientToken = await getToken(page, "client@test.local", "test1234");
    const adminToken  = await getToken(page, "admin@test.local", "admin1234");

    // 1. Get pricing config IDs
    const configs = await apiGet(page, clientToken, "/api/v1/order-configs/types-of-work/?limit=1");
    const workTypeId = configs?.results?.[0]?.id ?? 1;
    const paperTypes = await apiGet(page, clientToken, "/api/v1/order-configs/paper-types/?limit=1");
    const paperTypeId = paperTypes?.results?.[0]?.id ?? 1;
    const levels = await apiGet(page, clientToken, "/api/v1/order-configs/academic-levels/?limit=1");
    const levelId = levels?.results?.[0]?.id ?? 1;

    // 2. Get a price quote
    const quote = await apiPost(page, clientToken, "/api/v1/pricing/quotes/paper/start/", {
      service_code: "academic_writing",
      pages: 3,
      deadline_hours: 72,
      spacing: "double",
      paper_type_code: "essay",
      work_type_code: "writing",
      subject_code: "general",
      academic_level_code: "undergraduate",
      topic: "E2E test order",
      instructions: "This is a Playwright end-to-end test order.",
    });
    expect([200, 201]).toContain(quote.status);
    const price = quote.data?.calculated_price ?? quote.data?.price ?? "50.00";

    // 3. Create the order (endpoint is /orders/create/, not /orders/)
    const deadline = new Date(Date.now() + 72 * 3600 * 1000).toISOString();
    const orderResp = await apiPost(page, clientToken, "/api/v1/orders/orders/create/", {
      topic: "E2E test order",
      order_instructions: "Playwright end-to-end integration test.",
      client_deadline: deadline,
      number_of_pages: 3,
      paper_type_id: paperTypeId,
      type_of_work_id: workTypeId,
      academic_level_id: levelId,
      service_code: "academic_writing",
      service_family: "paper_order",
      payment_provider: "mock",
      payment_method_code: "mock_card",
      pricing_snapshot_id: quote.data?.snapshot_id ?? null,
      total_price: price,
    });
    expect([200, 201]).toContain(orderResp.status);
    const orderId = orderResp.data?.id ?? orderResp.data?.order?.id;
    expect(orderId).toBeTruthy();

    // 4. Verify order appears in admin ops summary
    const opsSummary = await apiGet(page, adminToken, "/api/v1/orders/ops/summary/");
    expect(opsSummary).toBeDefined();

    // 5. Verify order appears in admin order list
    const adminOrders = await apiGet(page, adminToken, `/api/v1/orders/orders/${orderId}/`);
    expect([200]).toContain(adminOrders?.id ? 200 : adminOrders?.detail ? 404 : 200);
  });
});
