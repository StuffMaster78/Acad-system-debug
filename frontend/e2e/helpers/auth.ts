import { Page, expect } from "@playwright/test";

export const USERS = {
  client:     { email: "client@test.local",   password: "test1234",  role: "client"     },
  writer:     { email: "writer@test.local",   password: "test1234",  role: "writer"     },
  admin:      { email: "admin@test.local",    password: "admin1234", role: "admin"      },
  editor:     { email: "editor@test.local",   password: "admin1234", role: "editor"     },
  support:    { email: "support@test.local",  password: "admin1234", role: "support"    },
  superadmin: { email: "rickawino@gmail.com", password: "admin1234", role: "superadmin" },
} as const;

export type UserRole = keyof typeof USERS;

/** Log in and wait until the dashboard is rendered. */
export async function login(page: Page, role: UserRole = "client") {
  const { email, password } = USERS[role];
  await page.goto("/");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in|log in/i }).click();
  // Wait for the redirect to role dashboard
  await page.waitForURL(`**/${role}**`, { timeout: 10_000 });
}

/** Log out from any authenticated page. */
export async function logout(page: Page) {
  // Try the user-menu logout button
  const userMenu = page.locator("[data-testid='user-menu'], button[aria-label*='user'], button[aria-label*='account']").first();
  if (await userMenu.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await userMenu.click();
  }
  const logoutBtn = page.getByRole("button", { name: /log out|sign out/i });
  if (await logoutBtn.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await logoutBtn.click();
    await page.waitForURL("**/login**", { timeout: 8_000 });
  } else {
    await page.goto("/");
  }
}

/** Call the backend login API directly and inject the token into localStorage
 *  so tests can skip the UI login form when testing non-auth flows. */
export async function apiLogin(page: Page, role: UserRole = "client") {
  const { email, password } = USERS[role];
  const resp = await page.evaluate(
    async ({ email, password }) => {
      const r = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      return r.json();
    },
    { email, password },
  );
  if (!resp.access_token) throw new Error(`API login failed for ${role}: ${JSON.stringify(resp)}`);
  await page.evaluate(
    ({ accessToken, refreshToken }) => {
      localStorage.setItem("ws_access_token", accessToken);
      localStorage.setItem("ws_refresh_token", refreshToken);
    },
    { accessToken: resp.access_token, refreshToken: resp.refresh_token },
  );
  return resp;
}
