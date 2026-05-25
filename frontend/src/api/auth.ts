import { api, apiPath } from "./client";
import type { AuthUser } from "@/types/roles";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
  user?: AuthUser;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    api.post<TokenPair>(apiPath("/auth/token/"), payload),
  refresh: (refresh: string) =>
    api.post<{ access: string }>(apiPath("/auth/token/refresh/"), { refresh }),
  me: () => api.get<AuthUser>(apiPath("/users/me/")),
  logout: () => api.post(apiPath("/auth/logout/")),
};
