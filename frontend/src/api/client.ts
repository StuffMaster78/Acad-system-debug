import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "@/stores/auth";

function getDeviceFingerprint(): string {
  const nav = navigator;
  const parts = [
    nav.userAgent,
    nav.language,
    String(screen.width) + "x" + String(screen.height),
    String(screen.colorDepth),
    Intl.DateTimeFormat().resolvedOptions().timeZone,
    String(nav.hardwareConcurrency ?? ""),
  ];
  const raw = parts.join("|");
  // Simple djb2 hash — stable across calls on the same browser
  let hash = 5381;
  for (let i = 0; i < raw.length; i++) {
    hash = ((hash << 5) + hash) ^ raw.charCodeAt(i);
  }
  return (hash >>> 0).toString(16);
}

const DEVICE_FINGERPRINT = getDeviceFingerprint();

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
const apiPrefix = import.meta.env.VITE_API_PREFIX || "/api/v1";
const ordersPrefix = import.meta.env.VITE_ORDERS_API_PREFIX || "/api/v1/orders";

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function normalizeApiOrigin(value: string): string {
  const trimmed = trimTrailingSlash(value.trim());
  if (!trimmed) return "";
  if (trimmed.endsWith(apiPrefix)) return trimTrailingSlash(trimmed.slice(0, -apiPrefix.length));
  return trimmed;
}

export const apiBaseOrigin = rawApiBaseUrl.trim()
  ? normalizeApiOrigin(rawApiBaseUrl)
  : "http://localhost:8000";
export const apiBasePrefix = apiPrefix;

export const api: AxiosInstance = axios.create({
  baseURL: apiBaseOrigin,
  headers: {
    "Content-Type": "application/json",
  },
});

export function apiPath(path: string): string {
  if (path.startsWith("http")) return path;
  if (path.startsWith("/api/")) return path;
  return `${apiBasePrefix}${path.startsWith("/") ? path : `/${path}`}`;
}

export function ordersApiPath(path: string): string {
  return `${ordersPrefix}${path.startsWith("/") ? path : `/${path}`}`;
}

const ANONYMOUS_AUTH_ENDPOINTS = [
  "/auth/login/",
  "/auth/register/",
  "/auth/register/confirm/",
  "/auth/register/resend/",
  "/auth/token/refresh/",
  "/auth/password/reset/request/",
  "/auth/password/reset/confirm/",
  "/auth/password/reset/validate-token/",
  "/auth/unlock/request/",
  "/auth/unlock/confirm/",
  "/auth/magic-link/request/",
  "/auth/magic-link/confirm/",
];

export function isAnonymousAuthRequest(url?: string): boolean {
  if (!url) return false;
  const path = url.split("?")[0].replace(/\/+$/, "/");
  return ANONYMOUS_AUTH_ENDPOINTS.some((endpoint) => path.endsWith(endpoint));
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = useAuthStore();
  // A stale access token must never poison anonymous authentication flows.
  // DRF authenticates before checking AllowAny, so an invalid Authorization
  // header makes a valid login fail with token_not_valid.
  if (auth.accessToken && !isAnonymousAuthRequest(config.url)) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  config.headers["X-Device-Fingerprint"] = DEVICE_FINGERPRINT;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const auth = useAuthStore();
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    if (error.response?.status === 401 && original && !original._retry) {
      // Anonymous auth failures belong to their form (bad credentials, expired
      // reset token, invalid magic link, etc.), not the refresh-token flow.
      if (isAnonymousAuthRequest(original.url)) {
        return Promise.reject(error);
      }

      // Preview sessions use fake tokens that always 401. Never clear them —
      // the whole point is to browse the app with mock data without a real backend session.
      if (auth.isPreviewSession) {
        return Promise.reject(error);
      }

      original._retry = true;
      const refreshed = await auth.refreshToken();
      if (refreshed) return api(original);
      // Refresh failed — clear session and redirect to login
      auth.clearSession();
      // Use location.replace so Back button doesn't loop; SPA shell reloads cleanly
      window.location.replace("/auth/login");
      return new Promise(() => {}); // halt the rejection chain
    }

    return Promise.reject(error);
  },
);
