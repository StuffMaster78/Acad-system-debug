import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { useRouter } from "vue-router";
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
  const router = useRouter();
  const accessToken = ref(window.localStorage.getItem(ACCESS_KEY) || "");
  const refresh = ref(window.localStorage.getItem(REFRESH_KEY) || "");
  const user = ref<AuthUser | null>(readUser());
  const isLoading = ref(false);

  const isAuthenticated = computed(() => Boolean(accessToken.value));
  const isPreviewSession = computed(() => accessToken.value.startsWith("dev-preview-"));
  const role = computed<UserRole | null>(() => user.value?.role ?? null);

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
  }

  async function logout() {
    if (isPreviewSession.value) {
      clearSession();
      router.push("/auth/login");
      return;
    }

    try {
      await authApi.logout();
    } finally {
      clearSession();
      router.push("/auth/login");
    }
  }

  function adoptSession(tokens: { access: string; refresh: string }, nextUser: AuthUser) {
    persist(tokens, nextUser);
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

  return {
    accessToken,
    refresh,
    user,
    role,
    isAuthenticated,
    isPreviewSession,
    isLoading,
    login,
    loadMe,
    refreshToken,
    logout,
    adoptSession,
    clearSession,
    previewAs,
    updateUser,
  };
});
