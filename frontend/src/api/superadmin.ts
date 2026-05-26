import { api, apiPath } from "./client";
import type {
  CrossTenantAnalyticsResponse,
  SuperadminAppeal,
  SuperadminDashboardStats,
  SuperadminLog,
  SuperadminUser,
  TenantComparisonResponse,
  TenantListResponse,
} from "@/types/superadmin";
import type { UserRole } from "@/types/roles";

type ListResponse<T> = T[] | { results: T[] };

export const superadminApi = {
  dashboard: () =>
    api.get<SuperadminDashboardStats>(apiPath("/superadmin-management/dashboard/")),
  tenants: (params?: Record<string, unknown>) =>
    api.get<TenantListResponse>(
      apiPath("/superadmin-management/tenants/list_tenants/"),
      { params },
    ),
  tenantComparison: () =>
    api.get<TenantComparisonResponse>(
      apiPath("/superadmin-management/tenants/comparison/"),
    ),
  crossTenantAnalytics: (days = 30) =>
    api.get<CrossTenantAnalyticsResponse>(
      apiPath("/superadmin-management/tenants/cross-tenant-analytics/"),
      { params: { days } },
    ),
  users: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SuperadminUser>>(
      apiPath("/superadmin-management/users/"),
      { params },
    ),
  suspendUser: (user_id: number, reason: string) =>
    api.post(apiPath("/superadmin-management/users/suspend_user/"), {
      user_id,
      reason,
    }),
  reactivateUser: (user_id: number) =>
    api.post(apiPath("/superadmin-management/users/reactivate_user/"), {
      user_id,
    }),
  changeUserRole: (user_id: number, new_role: UserRole) =>
    api.post(apiPath("/superadmin-management/users/change_user_role/"), {
      user_id,
      new_role,
    }),
  logs: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SuperadminLog>>(
      apiPath("/superadmin-management/logs/"),
      { params },
    ),
  appeals: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SuperadminAppeal>>(
      apiPath("/superadmin-management/appeals/"),
      { params },
    ),
  pendingAppeals: () =>
    api.get<SuperadminAppeal[]>(
      apiPath("/superadmin-management/appeals/pending/"),
    ),
  approveAppeal: (appealId: number) =>
    api.post(apiPath(`/superadmin-management/appeals/${appealId}/approve/`), {}),
  rejectAppeal: (appealId: number) =>
    api.post(apiPath(`/superadmin-management/appeals/${appealId}/reject/`), {}),
};
