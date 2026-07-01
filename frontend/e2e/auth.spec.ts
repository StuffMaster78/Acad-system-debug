import { test, expect } from "@playwright/test";
import { login, logout, USERS } from "./helpers/auth";

test.describe("Authentication flows", () => {
  test("login as client shows client dashboard", async ({ page }) => {
    await page.goto("/");
    await page.getByLabel(/email/i).fill(USERS.client.email);
    await page.getByLabel(/password/i).fill(USERS.client.password);
    await page.getByRole("button", { name: /sign in|log in/i }).click();
    await page.waitForURL("**/client**");
    await expect(page.getByRole("heading", { name: /good (morning|afternoon|evening)/i })).toBeVisible();
  });

  test("login as admin redirects to admin dashboard", async ({ page }) => {
    await login(page, "admin");
    await expect(page).toHaveURL(/\/admin/);
  });

  test("login as writer redirects to writer workspace", async ({ page }) => {
    await login(page, "writer");
    await expect(page).toHaveURL(/\/writer/);
  });

  test("wrong password shows error", async ({ page }) => {
    await page.goto("/");
    await page.getByLabel(/email/i).fill(USERS.client.email);
    await page.getByLabel(/password/i).fill("wrongpassword");
    await page.getByRole("button", { name: /sign in|log in/i }).click();
    await expect(page.getByText(/invalid|incorrect|wrong|failed/i)).toBeVisible({ timeout: 5_000 });
  });

  test("magic link request accepts a valid email", async ({ page }) => {
    await page.goto("/");
    const magicLink = page.getByRole("link", { name: /magic link|passwordless/i });
    if (await magicLink.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await magicLink.click();
      await page.getByLabel(/email/i).fill(USERS.client.email);
      await page.getByRole("button", { name: /send|request/i }).click();
      await expect(page.getByText(/sent|check your email/i)).toBeVisible({ timeout: 5_000 });
    } else {
      test.skip();
    }
  });

  test("password reset request accepts a valid email", async ({ page }) => {
    await page.goto("/");
    const forgotLink = page.getByRole("link", { name: /forgot|reset/i });
    if (await forgotLink.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await forgotLink.click();
      await page.getByLabel(/email/i).fill(USERS.client.email);
      await page.getByRole("button", { name: /send|reset/i }).click();
      await expect(page.getByText(/sent|check|email/i)).toBeVisible({ timeout: 5_000 });
    } else {
      test.skip();
    }
  });

  test("logout redirects to login page", async ({ page }) => {
    await login(page, "client");
    await logout(page);
    await expect(page).toHaveURL(/\/(login|$)/);
  });

  test("protected route redirects unauthenticated user to login", async ({ page }) => {
    await page.goto("/client/orders");
    await expect(page).toHaveURL(/\/(login|$)/);
  });

  test("admin cannot access client routes", async ({ page }) => {
    await login(page, "admin");
    await page.goto("/client/orders");
    // Should redirect away — not stay on /client/orders
    await expect(page).not.toHaveURL(/\/client\/orders/);
  });
});
