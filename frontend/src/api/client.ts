import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "@/stores/auth";

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
      original._retry = true;
      const refreshed = await auth.refreshToken();
      if (refreshed) return api(original);
    }

    return Promise.reject(error);
  },
);
