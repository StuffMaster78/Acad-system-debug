import type { UserRole } from "@/types/roles";

export type AdminAccessTone = "neutral" | "good" | "warn" | "risk";

export interface AdminAccessMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: AdminAccessTone;
}

export interface AdminWebsiteSummary {
  id: number;
  name: string;
  domain?: string;
}

export interface AdminManagedUser {
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
  is_staff?: boolean;
  is_superuser?: boolean;
  is_suspended?: boolean;
  is_blacklisted?: boolean;
  is_on_probation?: boolean;
  date_joined?: string;
  last_login?: string | null;
  website?: AdminWebsiteSummary | null;
  website_name?: string | null;
}

export interface AdminUserStats {
  total_users?: number;
  by_role?: Partial<Record<UserRole, number>>;
  active_users?: number;
  suspended_users?: number;
  blacklisted_users?: number;
  on_probation?: number;
}

export interface ImpersonationTokenResponse {
  success: boolean;
  token: string;
  expires_in_hours: number;
}

export interface ImpersonationStartResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    email: string;
    username?: string;
    full_name?: string;
    role: UserRole;
  };
  impersonation: {
    is_impersonation: boolean;
    impersonated_by?: Record<string, unknown>;
    started_at?: string;
  };
  expires_in: number;
}

export interface ImpersonationStatusResponse {
  is_impersonating: boolean;
  impersonator?: Record<string, unknown> | null;
}

export interface DuplicateAccountUser {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  website?: AdminWebsiteSummary | null;
  is_active?: boolean;
  is_suspended?: boolean;
  is_blacklisted?: boolean;
}

export interface DuplicateAccountGroup {
  user_ids: number[];
  users: DuplicateAccountUser[];
  websites?: AdminWebsiteSummary[];
  signals: string[] | Record<string, unknown>;
  detection_types?: string[];
  confidence: "low" | "medium" | "high" | string;
  match_count?: number;
}

export interface DuplicateStatsResponse {
  clients?: { suspected_groups?: number; users_involved?: number };
  writers?: { suspected_groups?: number; users_involved?: number };
  total?: { suspected_groups?: number; users_involved?: number };
}

export interface ProfileUpdateRequestRecord {
  id: number;
  user?: number | AdminManagedUser | Record<string, unknown>;
  requested_changes?: Record<string, unknown>;
  changes?: Record<string, unknown>;
  status?: string;
  reason?: string;
  created_at?: string;
  updated_at?: string;
  reviewed_at?: string | null;
  [key: string]: unknown;
}

export interface BlacklistedEmailRecord {
  id?: number;
  email: string;
  reason?: string;
  date_added?: string;
}
