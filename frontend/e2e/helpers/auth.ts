import { Page } from "@playwright/test";

export const USERS = {
  client:     { email: "client@test.local",   password: "test1234",  role: "client"     },
  writer:     { email: "writer@test.local",   password: "test1234",  role: "writer"     },
  admin:      { email: "admin@test.local",    password: "admin1234", role: "admin"      },
  editor:     { email: "editor@test.local",   password: "admin1234", role: "editor"     },
  support:    { email: "support@test.local",  password: "admin1234", role: "support"    },
  superadmin: { email: "rickawino@gmail.com", password: "admin1234", role: "superadmin" },
} as const;

export type UserRole = keyof typeof USERS;

const LS_ACCESS  = "writing_system.access";
const LS_REFRESH = "writing_system.refresh";
const LS_USER    = "writing_system.user";

const DJANGO_BASE = "http://localhost:8000";

const ROLE_HOME: Record<UserRole, string> = {
  client: "/client", writer: "/writer", admin: "/admin",
  editor: "/editor", support: "/support", superadmin: "/superadmin",
};

// Module-level token cache — persists across tests in the same worker process.
// Login API is called at most once per role per test run (avoids login throttle).
type CachedCreds = { access_token: string; refresh_token: string; user: Record<string, unknown>; expires: number };
const _tokenCache = new Map<UserRole, CachedCreds>();

/**
 * Log in and land on the role dashboard.
 *
 * Uses Playwright's API request context (Node.js side) to hit Django directly —
 * no CORS restrictions, no Vite proxy, no throttle accumulation from browser-side
 * fetch calls. Tokens are injected into localStorage so the SPA picks them up.
 */
export async function login(page: Page, role: UserRole = "client") {
  const resp = await apiLogin(page, role);
  await page.goto(ROLE_HOME[role]);
  await page.waitForURL(`**/${role}**`, { timeout: 15_000 });
  return resp;
}

/**
 * Log in via the UI form — use only in tests that specifically test the login UI.
 */
export async function loginViaForm(page: Page, role: UserRole = "client") {
  const { email, password } = USERS[role];
  await page.goto("/auth/login");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL(`**/${role}**`, { timeout: 15_000 });
}

/**
 * Authenticate via the Django API using Playwright's request context
 * (runs in Node.js — bypasses browser CORS and Vite proxy).
 * Tokens are cached in-process so the login endpoint is called at most once per
 * role per test run, keeping well under the 10/min throttle.
 */
export async function apiLogin(page: Page, role: UserRole = "client") {
  let creds = _tokenCache.get(role);

  if (!creds || Date.now() > creds.expires) {
    const { email, password } = USERS[role];

    const loginResp = await page.request.post(`${DJANGO_BASE}/api/v1/auth/login/`, {
      data: { email, password },
      headers: { "Content-Type": "application/json" },
    });
    const loginData = await loginResp.json();
    if (!loginData.access_token) {
      throw new Error(`apiLogin failed for ${role}: ${JSON.stringify(loginData)}`);
    }

    const meResp = await page.request.get(`${DJANGO_BASE}/api/v1/users/users/me/`, {
      headers: { Authorization: `Bearer ${loginData.access_token}` },
    });
    const meData = await meResp.json();

    creds = {
      access_token:  loginData.access_token as string,
      refresh_token: loginData.refresh_token as string ?? "",
      user: meData,
      expires: Date.now() + 20 * 60 * 1000, // cache for 20 min (within JWT expiry)
    };
    _tokenCache.set(role, creds);
  }

  // Ensure we're on a same-origin page before touching localStorage
  if (page.url() === "about:blank" || !page.url().includes("localhost")) {
    await page.goto("/auth/login");
  }

  await page.evaluate(
    ({ lsAccess, lsRefresh, lsUser, access, refresh, user }) => {
      localStorage.setItem(lsAccess, access);
      localStorage.setItem(lsRefresh, refresh);
      localStorage.setItem(lsUser, JSON.stringify(user));
    },
    {
      lsAccess: LS_ACCESS, lsRefresh: LS_REFRESH, lsUser: LS_USER,
      access:  creds.access_token,
      refresh: creds.refresh_token,
      user:    creds.user,
    },
  );

  return { access_token: creds.access_token, user: creds.user };
}

/** Log out from any authenticated page. */
export async function logout(page: Page) {
  const userMenu = page.locator("[data-testid='user-menu'], button[aria-label*='user'], button[aria-label*='account']").first();
  if (await userMenu.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await userMenu.click();
  }
  const logoutBtn = page.getByRole("button", { name: /log out|sign out/i });
  if (await logoutBtn.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await logoutBtn.click();
    await page.waitForURL("**/login**", { timeout: 8_000 });
  } else {
    await page.goto("/auth/login");
  }
}
