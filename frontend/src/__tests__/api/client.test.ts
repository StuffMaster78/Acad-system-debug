import { beforeEach, describe, expect, it } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import type { InternalAxiosRequestConfig } from "axios";

import { api, isAnonymousAuthRequest } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

describe("API client anonymous authentication requests", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it.each([
    "/api/v1/auth/login/",
    "/api/v1/auth/register/",
    "/api/v1/auth/register/confirm/",
    "/api/v1/auth/token/refresh/",
    "/api/v1/auth/password/reset/request/",
    "/api/v1/auth/magic-link/confirm/?next=/client",
  ])("does not attach a stored bearer token to %s", (url) => {
    expect(isAnonymousAuthRequest(url)).toBe(true);
  });

  it.each([
    "/api/v1/auth/logout/",
    "/api/v1/auth/password/change/",
    "/api/v1/auth/sessions/",
    "/api/v1/users/users/me/",
  ])("keeps authentication on protected request %s", (url) => {
    expect(isAnonymousAuthRequest(url)).toBe(false);
  });

  it("omits a stale stored token from login while retaining it for protected APIs", async () => {
    const auth = useAuthStore();
    auth.previewAs("admin");

    const seen: Array<string | undefined> = [];
    const adapter = async (config: InternalAxiosRequestConfig) => {
      seen.push(config.headers?.Authorization?.toString());
      return { data: {}, status: 200, statusText: "OK", headers: {}, config };
    };

    await api.post("/api/v1/auth/login/", {}, { adapter });
    await api.get("/api/v1/users/users/me/", { adapter });

    expect(seen).toEqual([undefined, "Bearer dev-preview-admin"]);
  });
});
