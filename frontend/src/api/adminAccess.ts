import { api, apiPath } from "./client";
import type {
  AdminManagedUser,
  AdminUserStats,
  BlacklistedEmailRecord,
  DuplicateAccountGroup,
  DuplicateStatsResponse,
  ImpersonationStartResponse,
  ImpersonationStatusResponse,
  ImpersonationTokenResponse,
  ProfileUpdateRequestRecord,
} from "@/types/adminAccess";
import type { UserRole } from "@/types/roles";

type ListResponse<T> = T[] | { results: T[] };

export interface CreateUserPayload {
  username: string;
  email: string;
  role: UserRole;
  password?: string;
  first_name?: string;
  last_name?: string;
  website?: number | null;
  send_invite?: boolean;
}

export interface CreateUserResponse extends AdminManagedUser {
  invite_link?: string;
}

export interface DuplicateDetectResponse {
  count: number;
  results: DuplicateAccountGroup[];
}

export const adminAccessApi = {
  users: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminManagedUser>>(
      apiPath("/admin-management/user-management/"),
      { params },
    ),
  user: (userId: number) =>
    api.get<AdminManagedUser>(
      apiPath(`/admin-management/user-management/${userId}/`),
    ),
  stats: () =>
    api.get<AdminUserStats>(
      apiPath("/admin-management/user-management/stats/"),
    ),
  createUser: (payload: CreateUserPayload) =>
    api.post<CreateUserResponse>(
      apiPath("/admin-management/user-management/"),
      payload,
    ),
  profileUpdateRequests: (params?: Record<string, unknown>) =>
    api.get<ListResponse<ProfileUpdateRequestRecord>>(
      apiPath("/client-management/profile-update-requests/admin/"),
      { params },
    ),
  blacklistedEmails: () =>
    api.get<ListResponse<BlacklistedEmailRecord>>(
      apiPath("/client-management/blacklist/"),
    ),
  addBlacklistedEmail: (email: string, reason: string) =>
    api.post(apiPath("/client-management/blacklist/add/"), { email, reason }),
  removeBlacklistedEmail: (email: string) =>
    api.delete(apiPath("/client-management/blacklist/remove/"), {
      data: { email },
    }),
  duplicateStats: () =>
    api.get<DuplicateStatsResponse>(
      apiPath("/admin-management/duplicate-detection/stats/"),
    ),
  detectDuplicates: (params?: Record<string, unknown>) =>
    api.get<DuplicateDetectResponse>(
      apiPath("/admin-management/duplicate-detection/detect/"),
      { params },
    ),
  suspend: (userId: number, reason: string, duration_days = 30) =>
    api.post(apiPath(`/admin-management/user-management/${userId}/suspend/`), {
      reason,
      duration_days,
    }),
  unsuspend: (userId: number, reason: string) =>
    api.post(apiPath(`/admin-management/user-management/${userId}/unsuspend/`), {
      reason,
    }),
  resetPassword: (userId: number) =>
    api.post(apiPath(`/admin-management/user-management/${userId}/reset_password/`), {}),
  changeRole: (userId: number, role: UserRole) =>
    api.post(apiPath(`/admin-management/user-management/${userId}/change_role/`), {
      role,
    }),
  promoteToAdmin: (userId: number) =>
    api.post(apiPath(`/admin-management/user-management/${userId}/promote_to_admin/`), {}),
  unlockUser: (userId: number) =>
    api.post(apiPath(`/auth/admin/users/${userId}/unlock/`), {}),
  kickoutUser: (userId: number, reason: string) =>
    api.post(apiPath(`/auth/admin/users/${userId}/kickout/`), {
      reason,
    }),
  impersonationStatus: () =>
    api.get<ImpersonationStatusResponse>(
      apiPath("/auth/impersonation/status/"),
    ),
  createImpersonationToken: (target_user_id: number, reason: string) =>
    api.post<ImpersonationTokenResponse>(
      apiPath("/auth/impersonation/token/"),
      { target_user_id, reason },
    ),
  startImpersonation: (token: string, reason: string) =>
    api.post<ImpersonationStartResponse>(
      apiPath("/auth/impersonation/start/"),
      { token, reason },
    ),
  endImpersonation: (reason: string, close_tab = false) =>
    api.post(
      apiPath("/auth/impersonation/end/"),
      { reason, close_tab },
    ),
};
