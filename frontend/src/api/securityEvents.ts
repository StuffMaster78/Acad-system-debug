import { api, apiPath } from "./client";

export interface SecurityEvent {
  id: number;
  event_type: string;
  severity: string;
  ip_address: string | null;
  location: string | null;
  device: string | null;
  created_at: string;
}

export const securityEventsApi = {
  list: () =>
    api.get<SecurityEvent[]>(apiPath("/auth/security-events/")),
};
