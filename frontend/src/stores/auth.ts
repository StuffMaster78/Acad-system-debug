import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { authApi, type LoginPayload } from "@/api/auth";
import type { AuthUser, UserRole } from "@/types/roles";

export class MfaRequiredError extends Error {
  constructor(public readonly userId: number) {
    super("mfa_required");
  }
}

const ACCESS_KEY = "writing_system.access";
const REFRESH_KEY = "writing_system.refresh";
const USER_KEY = "writing_system.user";
const IMPERSONATION_ORIGIN_KEY = "writing_system.impersonation_origin";

function readUser(): AuthUser | null {
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore("auth", () => {
  // router is NOT stored here — useRouter() is called at store-creation time which
  // can happen before app.use(router) in main.ts (the axios interceptor creates the
  // store on the first API call). Instead, navigate via window.location.replace so
  // redirects always work regardless of when the store is instantiated.
  const accessToken = ref(window.localStorage.getItem(ACCESS_KEY) || "");
  const refresh = ref(window.localStorage.getItem(REFRESH_KEY) || "");
  const user = ref<AuthUser | null>(readUser());
  const isLoading = ref(false);

  const isAuthenticated = computed(() => Boolean(accessToken.value));
  const isPreviewSession = computed(() => accessToken.value.startsWith("dev-preview-"));
  const role = computed<UserRole | null>(() => user.value?.role ?? null);
  const isImpersonating = computed(
    () => Boolean(window.localStorage.getItem(IMPERSONATION_ORIGIN_KEY))
  );

  function persist(tokens: { access?: string; refresh?: string }, nextUser?: AuthUser) {
    if (tokens.access) {
      accessToken.value = tokens.access;
      window.localStorage.setItem(ACCESS_KEY, tokens.access);
    }
    if (tokens.refresh) {
      refresh.value = tokens.refresh;
      window.localStorage.setItem(REFRESH_KEY, tokens.refresh);
    }
    if (nextUser) {
      user.value = nextUser;
      window.localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    }
  }

  async function login(payload: LoginPayload) {
    isLoading.value = true;
    try {
      const { data } = await authApi.login(payload);
      if (data.mfa_required) {
        throw new MfaRequiredError(data.user_id ?? 0);
      }
      if (!data.access_token) throw new Error("No access token in login response");
      persist({ access: data.access_token, refresh: data.refresh_token });
      await loadMe();
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMe() {
    const { data } = await authApi.me();
    user.value = data;
    window.localStorage.setItem(USER_KEY, JSON.stringify(data));
    return data;
  }

  async function refreshToken() {
    if (!refresh.value) return false;
    try {
      const { data } = await authApi.refresh(refresh.value);
      persist({ access: data.access });
      return true;
    } catch {
      clearSession();
      return false;
    }
  }

  function clearSession() {
    accessToken.value = "";
    refresh.value = "";
    user.value = null;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
    window.localStorage.removeItem(USER_KEY);
    window.localStorage.removeItem(IMPERSONATION_ORIGIN_KEY);
    // Remove dashboard first-visit markers so they don't leak between sessions
    // (preview uses id=0 which would otherwise persist as ws-visited-0)
    Object.keys(window.localStorage)
      .filter((k) => k.startsWith("ws-visited-"))
      .forEach((k) => window.localStorage.removeItem(k));
  }

  async function logout() {
    if (isPreviewSession.value) {
      clearSession();
      window.location.replace("/auth/login");
      return;
    }

    try {
      await authApi.logout();
    } finally {
      clearSession();
      window.location.replace("/auth/login");
    }
  }

  function adoptSession(tokens: { access: string; refresh: string }, nextUser: AuthUser) {
    // Snapshot the current session before switching so impersonation can be reversed.
    if (!window.localStorage.getItem(IMPERSONATION_ORIGIN_KEY)) {
      window.localStorage.setItem(
        IMPERSONATION_ORIGIN_KEY,
        JSON.stringify({
          access: accessToken.value,
          refresh: refresh.value,
          user: user.value,
        }),
      );
    }
    persist(tokens, nextUser);
  }

  function restoreFromImpersonation(serverSession?: {
    access: string;
    refresh: string;
    user: AuthUser;
  }) {
    const raw = window.localStorage.getItem(IMPERSONATION_ORIGIN_KEY);
    window.localStorage.removeItem(IMPERSONATION_ORIGIN_KEY);

    if (serverSession) {
      persist(
        {
          access: serverSession.access,
          refresh: serverSession.refresh,
        },
        serverSession.user,
      );
      return;
    }

    if (!raw) return;
    const origin = JSON.parse(raw) as {
      access: string;
      refresh: string;
      user: AuthUser;
    };
    persist({ access: origin.access, refresh: origin.refresh }, origin.user);
  }

  function previewAs(roleName: AuthUser["role"]) {
    if (!import.meta.env.DEV) return;
    persist(
      {
        access: `dev-preview-${roleName}`,
        refresh: `dev-preview-refresh-${roleName}`,
      },
      {
        id: 0,
        email: `${roleName}@preview.local`,
        full_name: `${roleName} preview`,
        role: roleName,
      },
    );
  }

  function updateUser(patch: Partial<AuthUser>) {
    if (!user.value) return;
    user.value = { ...user.value, ...patch };
    window.localStorage.setItem(USER_KEY, JSON.stringify(user.value));
  }

  async function loginWithMagicLink(token: string) {
    isLoading.value = true;
    try {
      const { data } = await authApi.confirmMagicLink(token);
      if (!data.access_token) throw new Error("No access token in magic link response");
      persist({ access: data.access_token, refresh: data.refresh_token });
      await loadMe();
    } finally {
      isLoading.value = false;
    }
  }

  async function adoptTokens(access: string, refresh: string) {
    persist({ access, refresh });
    await loadMe();
  }

  return {
    accessToken,
    refresh,
    user,
    role,
    isAuthenticated,
    isPreviewSession,
    isImpersonating,
    isLoading,
    login,
    loadMe,
    refreshToken,
    logout,
    adoptSession,
    restoreFromImpersonation,
    clearSession,
    previewAs,
    updateUser,
    loginWithMagicLink,
    adoptTokens,
  };
});
