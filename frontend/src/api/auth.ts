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

export interface MagicLinkConfirmResponse extends LoginResponse {}

export interface AdminMagicLinkResponse {
  success: boolean;
  user_id: number;
  magic_url: string;
  expires_minutes: number;
}

export interface AdminPasswordResetLinkResponse {
  success: boolean;
  user_id: number;
  reset_link: string;
  otp_code: string;
  token: string;
  expires_hours: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  username: string;
  first_name?: string;
  last_name?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
  utm_term?: string;
  referrer?: string;
  landing_page?: string;
}

export interface RegisterResponse {
  success: boolean;
  user_id: number;
  message: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    api.post<RegisterResponse>(apiPath("/auth/register/"), payload),

  confirmRegistration: (token: string, otpCode: string) =>
    api.post<LoginResponse>(apiPath("/auth/register/confirm/"), {
      token,
      otp_code: otpCode,
    }),

  resendRegistration: (email: string) =>
    api.post(apiPath("/auth/register/resend/"), { email }),

  login: (payload: LoginPayload) =>
    api.post<LoginResponse>(apiPath("/auth/login/"), payload),
  refresh: (refresh: string) =>
    api.post<{ access: string }>(apiPath("/auth/token/refresh/"), { refresh }),
  me: () => api.get<AuthUser>(apiPath("/users/users/me/")),
  updateMe: (payload: UpdateMePayload) =>
    api.patch<AuthUser>(apiPath("/users/users/me/"), payload),
  changePassword: (payload: ChangePasswordPayload) =>
    api.post(apiPath("/auth/password/change/"), payload),
  forgotPassword: (email: string) =>
    api.post(apiPath("/auth/password/reset/request/"), { email }),
  resetPassword: (token: string, otpCode: string, newPassword: string) =>
    api.post(apiPath("/auth/password/reset/confirm/"), { token, otp_code: otpCode, new_password: newPassword }),
  // Magic link: user self-service (request + confirm)
  requestMagicLink: (email: string) =>
    api.post(apiPath("/auth/magic-link/request/"), { email }),
  confirmMagicLink: (token: string) =>
    api.post<MagicLinkConfirmResponse>(apiPath("/auth/magic-link/confirm/"), { token }),
  // Admin tools: generate auth links for a target user
  adminGenerateMagicLink: (userId: number) =>
    api.post<AdminMagicLinkResponse>(apiPath(`/auth/admin/users/${userId}/magic-link/`), {}),
  adminGeneratePasswordResetLink: (userId: number) =>
    api.post<AdminPasswordResetLinkResponse>(apiPath(`/auth/admin/users/${userId}/password-reset-link/`), {}),
  uploadAvatar: (file: File) => {
    const form = new FormData();
    form.append("avatar", file);
    return api.post<AuthUser>(apiPath("/users/users/me/avatar/"), form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  logout: () => api.post(apiPath("/auth/logout/")),
};
