import { api, apiPath } from "./client";

export interface ImpersonationTokenResponse {
  success: boolean;
  token: string;
  expires_in_hours: number;
}

export interface ImpersonationUserInfo {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role?: string | null;
}

export interface ImpersonationState {
  is_impersonation: boolean;
  impersonated_by?: Record<string, unknown>;
  started_at?: string;
}

export interface ImpersonationStartResponse {
  access_token: string;
  refresh_token: string;
  user: ImpersonationUserInfo;
  impersonation: ImpersonationState;
  expires_in: number;
}

export interface ImpersonationEndResponse {
  access_token?: string;
  refresh_token?: string;
  user?: ImpersonationUserInfo;
  message: string;
  close_tab: boolean;
}

export interface ImpersonationStatusResponse {
  is_impersonating: boolean;
  impersonator?: Record<string, unknown> | null;
}

export const impersonationApi = {
  createToken: (targetUserId: number, reason: string) =>
    api.post<ImpersonationTokenResponse>(
      apiPath("/auth/impersonation/token/"),
      { target_user_id: targetUserId, reason },
    ),

  start: (token: string, reason?: string) =>
    api.post<ImpersonationStartResponse>(
      apiPath("/auth/impersonation/start/"),
      { token, reason },
    ),

  end: (reason?: string) =>
    api.post<ImpersonationEndResponse>(
      apiPath("/auth/impersonation/end/"),
      { close_tab: false, reason },
    ),

  status: () =>
    api.get<ImpersonationStatusResponse>(
      apiPath("/auth/impersonation/status/"),
    ),
};
