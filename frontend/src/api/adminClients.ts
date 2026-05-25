import { api, apiPath } from "./client";
import type { UserRole } from "@/types/roles";

export interface AdminWebsiteSummary {
  id: number;
  name: string;
  domain?: string;
}

export interface AdminClientProfileRecord {
  id: number;
  user: number;
  client_username?: string;
  timezone?: string;
  country?: string | null;
  preferred_writers?: string[];
  loyalty_points?: number;
  loyalty_tier?: string | null;
  wallet_balance?: string | number;
  total_spent?: string | number;
  is_active?: boolean;
  is_suspended?: boolean;
  badges?: unknown[];
}

export interface AdminUserRecord {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  role: UserRole;
  role_display?: string;
  phone_number?: string | null;
  is_active: boolean;
  is_suspended?: boolean;
  is_blacklisted?: boolean;
  is_on_probation?: boolean;
  date_joined?: string;
  last_login?: string | null;
  website?: AdminWebsiteSummary | null;
}

export interface ProfileUpdateRequestRecord {
  id: number;
  client: number;
  client_username?: string;
  requested_changes: Record<string, unknown>;
  status: string;
  admin_response?: string;
  created_at: string;
  updated_at: string;
}

export interface BlacklistedEmailRecord {
  id: number;
  email: string;
  reason?: string;
  date_added?: string;
}

export interface ClientWalletRecord {
  available_balance?: string | number;
  wallet_balance?: string | number;
  balance?: string | number;
  transactions?: unknown[];
  entries?: unknown[];
}

export interface ClientActionPayload {
  action: "suspend" | "activate" | "deactivate";
}

export interface AdminActionResponse {
  message?: string;
  detail?: string;
  status?: string;
}

type ListResponse<T> = T[] | { results: T[] };

export const adminClientsApi = {
  profiles: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminClientProfileRecord>>(
      apiPath("/client-management/clients/"),
      { params },
    ),
  users: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminUserRecord>>(
      apiPath("/admin-management/user-management/"),
      { params },
    ),
  profileUpdateRequests: () =>
    api.get<ListResponse<ProfileUpdateRequestRecord>>(
      apiPath("/client-management/profile-update-requests/admin/"),
    ),
  blacklist: () =>
    api.get<ListResponse<BlacklistedEmailRecord>>(
      apiPath("/client-management/blacklist/"),
    ),
  wallet: (clientId: number) =>
    api.get<ClientWalletRecord>(
      apiPath(`/client-management/clients/${clientId}/wallet/`),
    ),
  action: (clientId: number, payload: ClientActionPayload) =>
    api.post<AdminActionResponse>(
      apiPath(`/client-management/clients/${clientId}/actions/`),
      payload,
    ),
  suspendUser: (userId: number, reason: string) =>
    api.post<AdminActionResponse>(
      apiPath(`/admin-management/user-management/${userId}/suspend/`),
      { reason },
    ),
  unsuspendUser: (userId: number, reason: string) =>
    api.post<AdminActionResponse>(
      apiPath(`/admin-management/user-management/${userId}/unsuspend/`),
      { reason },
    ),
  resetPassword: (userId: number) =>
    api.post<AdminActionResponse>(
      apiPath(`/admin-management/user-management/${userId}/reset_password/`),
      {},
    ),
};
