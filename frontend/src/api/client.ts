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

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const apiPrefix = import.meta.env.VITE_API_PREFIX || "/api/v1";
const ordersPrefix = import.meta.env.VITE_ORDERS_API_PREFIX || "/api/v1";

export const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function apiPath(path: string): string {
  if (path.startsWith("http")) return path;
  if (path.startsWith("/api/")) return path;
  return `${apiPrefix}${path.startsWith("/") ? path : `/${path}`}`;
}

export function ordersApiPath(path: string): string {
  return `${ordersPrefix}${path.startsWith("/") ? path : `/${path}`}`;
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
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
      // Preview sessions use fake tokens that always 401. Never clear them —
      // the whole point is to browse the app with mock data without a real backend session.
      if (auth.isPreviewSession) {
        return Promise.reject(error);
      }

      original._retry = true;
      const refreshed = await auth.refreshToken();
      if (refreshed) return api(original);
      // Refresh failed — clear session and redirect via router (no full-page reload)
      auth.clearSession();
      // Lazy import to avoid circular dep: api → router → stores → api
      import("@/router").then(({ router }) => {
        router.push({ name: "login" }).catch(() => undefined);
      });
      return new Promise(() => {}); // halt the rejection chain
    }

    return Promise.reject(error);
  },
);
