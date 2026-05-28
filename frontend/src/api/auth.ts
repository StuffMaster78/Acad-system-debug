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

export interface LoginResponse {
  success: boolean;
  mfa_required: boolean;
  access_token?: string;
  refresh_token?: string;
  session_id?: number;
  user_id?: number;
}

export interface UpdateMePayload {
  full_name?: string;
  bio?: string | null;
  phone?: string | null;
  location?: string | null;
  timezone?: string | null;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    api.post<LoginResponse>(apiPath("/auth/login/"), payload),
  refresh: (refresh: string) =>
    api.post<{ access: string }>(apiPath("/auth/token/refresh/"), { refresh }),
  me: () => api.get<AuthUser>(apiPath("/users/me/")),
  updateMe: (payload: UpdateMePayload) =>
    api.patch<AuthUser>(apiPath("/users/me/"), payload),
  changePassword: (payload: ChangePasswordPayload) =>
    api.post(apiPath("/users/me/change-password/"), payload),
  forgotPassword: (email: string) =>
    api.post(apiPath("/auth/password/reset/request/"), { email }),
  resetPassword: (token: string, otpCode: string, newPassword: string) =>
    api.post(apiPath("/auth/password/reset/confirm/"), { token, otp_code: otpCode, new_password: newPassword }),
  uploadAvatar: (file: File) => {
    const form = new FormData();
    form.append("avatar", file);
    return api.post<AuthUser>(apiPath("/users/me/avatar/"), form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  logout: () => api.post(apiPath("/auth/logout/")),
};
