import { api, apiPath } from "./client";

export interface LoginSession {
  id: number;
  ip_address: string | null;
  user_agent: string;
  device_name: string | null;
  logged_in_at: string;
  last_activity_at?: string | null;
  is_active: boolean;
  session_type?: string;
}

export interface CurrentSession extends LoginSession {
  session_id: number;
  session_type: string;
  fingerprint_hash: string | null;
}

export const sessionsApi = {
  list: () =>
    api.get<LoginSession[]>(apiPath("/auth/sessions/")),

  current: () =>
    api.get<CurrentSession>(apiPath("/auth/sessions/current/")),

  revoke: (sessionId: number) =>
    api.post(apiPath("/auth/sessions/revoke/"), { session_id: sessionId }),

  revokeAll: () =>
    api.post(apiPath("/auth/sessions/revoke-all/"), { confirm: true }),
};
