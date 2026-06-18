import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";

vi.mock("vue-router", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/api/auth", () => ({
  authApi: { login: vi.fn(), logout: vi.fn(), me: vi.fn(), refresh: vi.fn() },
}));

import { useAuthStore } from "@/stores/auth";

const MOCK_USER = {
  id: 1, email: "admin@test.com", full_name: "Test Admin", role: "admin" as const,
};
const MOCK_TOKENS = { access: "access-token", refresh: "refresh-token" };

describe("auth store — state management", () => {
  beforeEach(() => { setActivePinia(createPinia()); localStorage.clear(); vi.resetAllMocks(); });

  it("starts unauthenticated", () => {
    const auth = useAuthStore();
    expect(auth.isAuthenticated).toBe(false);
    expect(auth.role).toBeNull();
    expect(auth.user).toBeNull();
  });

  it("adoptSession sets authenticated state and user", () => {
    const auth = useAuthStore();
    auth.adoptSession(MOCK_TOKENS, MOCK_USER);
    expect(auth.isAuthenticated).toBe(true);
    expect(auth.role).toBe("admin");
    expect(auth.user?.email).toBe("admin@test.com");
  });

  it("restores fresh server tokens after impersonation", () => {
    const auth = useAuthStore();
    auth.adoptSession(MOCK_TOKENS, MOCK_USER);
    auth.adoptSession(
      { access: "impersonated-access", refresh: "impersonated-refresh" },
      { ...MOCK_USER, id: 2, email: "client@test.com", role: "client" },
    );

    auth.restoreFromImpersonation({
      access: "fresh-admin-access",
      refresh: "fresh-admin-refresh",
      user: MOCK_USER,
    });

    expect(auth.accessToken).toBe("fresh-admin-access");
    expect(auth.refresh).toBe("fresh-admin-refresh");
    expect(auth.user).toEqual(MOCK_USER);
    expect(auth.isImpersonating).toBe(false);
  });

  it("clearSession resets to unauthenticated", () => {
    const auth = useAuthStore();
    auth.adoptSession(MOCK_TOKENS, MOCK_USER);
    auth.clearSession();
    expect(auth.isAuthenticated).toBe(false);
    expect(auth.user).toBeNull();
    expect(auth.role).toBeNull();
  });

  it("previewAs sets preview flag and correct role", () => {
    const auth = useAuthStore();
    auth.previewAs("client");
    expect(auth.isPreviewSession).toBe(true);
    expect(auth.role).toBe("client");
  });

  it("previewAs works for all roles", () => {
    const roles = ["client", "writer", "editor", "support", "admin", "superadmin"] as const;
    for (const role of roles) {
      setActivePinia(createPinia());
      const auth = useAuthStore();
      auth.previewAs(role);
      expect(auth.role).toBe(role);
      expect(auth.isPreviewSession).toBe(true);
    }
  });

  it("isPreviewSession is false for real tokens", () => {
    const auth = useAuthStore();
    auth.adoptSession(MOCK_TOKENS, MOCK_USER);
    expect(auth.isPreviewSession).toBe(false);
  });

  it("updateUser deep merges patch without losing other fields", () => {
    const auth = useAuthStore();
    auth.adoptSession(MOCK_TOKENS, MOCK_USER);
    auth.updateUser({ full_name: "New Name" });
    expect(auth.user?.full_name).toBe("New Name");
    expect(auth.user?.email).toBe("admin@test.com");
    expect(auth.user?.role).toBe("admin");
  });

  it("adoptSession with different roles reports correct role", () => {
    const roles = ["writer", "editor", "support"] as const;
    for (const role of roles) {
      setActivePinia(createPinia());
      const auth = useAuthStore();
      auth.adoptSession(MOCK_TOKENS, { ...MOCK_USER, role });
      expect(auth.role).toBe(role);
    }
  });
});
