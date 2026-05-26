import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { superadminApi } from "@/api/superadmin";
import { useAuthStore } from "@/stores/auth";
import type {
  CrossTenantAnalyticsResponse,
  SuperadminAppeal,
  SuperadminDashboardStats,
  SuperadminLog,
  SuperadminMetric,
  SuperadminUser,
  TenantSummary,
} from "@/types/superadmin";
import type { UserRole } from "@/types/roles";

type ListResponse<T> = T[] | { results?: T[] };

function normalizeList<T>(payload: ListResponse<T> | undefined): T[] {
  if (Array.isArray(payload)) return payload;
  return payload?.results ?? [];
}

function numberValue(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function money(value: unknown): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(numberValue(value));
}

function previewTenants(): TenantSummary[] {
  return [
    {
      id: 1,
      name: "WritePro Global",
      domain: "writepro.test",
      is_active: true,
      user_count: 1840,
      order_count: 12620,
      total_revenue: 782400,
      recent_orders_30d: 620,
      new_users_30d: 142,
      avg_order_value: 126,
      metrics: {
        users: { total: 1840, new_this_period: 142 },
        orders: { total: 620, completed: 571, completion_rate: 92.1 },
        revenue: { total: 782400, avg_per_order: 126 },
        disputes: { total: 8, resolution_rate: 87.5 },
        support: { total_tickets: 46, resolution_rate: 91.3 },
      },
    },
    {
      id: 2,
      name: "EssayDesk",
      domain: "essaydesk.test",
      is_active: true,
      user_count: 930,
      order_count: 6940,
      total_revenue: 402100,
      recent_orders_30d: 318,
      new_users_30d: 71,
      avg_order_value: 119,
      metrics: {
        users: { total: 930, new_this_period: 71 },
        orders: { total: 318, completed: 287, completion_rate: 90.3 },
        revenue: { total: 402100, avg_per_order: 119 },
        disputes: { total: 5, resolution_rate: 80 },
        support: { total_tickets: 29, resolution_rate: 86.2 },
      },
    },
    {
      id: 3,
      name: "CampusAssist",
      domain: "campusassist.test",
      is_active: false,
      user_count: 214,
      order_count: 1020,
      total_revenue: 59200,
      recent_orders_30d: 18,
      new_users_30d: 9,
      avg_order_value: 94,
    },
  ];
}

export const useSuperadminWorkspaceStore = defineStore("superadmin-workspace", () => {
  const dashboard = ref<SuperadminDashboardStats>({});
  const tenants = ref<TenantSummary[]>([]);
  const crossTenant = ref<CrossTenantAnalyticsResponse>({});
  const users = ref<SuperadminUser[]>([]);
  const logs = ref<SuperadminLog[]>([]);
  const appeals = ref<SuperadminAppeal[]>([]);
  const query = ref("");
  const selectedUserId = ref<number | null>(null);
  const roleDraft = ref<UserRole>("admin");
  const reason = ref("Platform governance review.");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const activeTenants = computed(() => tenants.value.filter((tenant) => tenant.is_active !== false));
  const inactiveTenants = computed(() => tenants.value.filter((tenant) => tenant.is_active === false));
  const pendingAppeals = computed(() => appeals.value.filter((appeal) => appeal.status === "pending"));
  const riskCount = computed(() =>
    numberValue(dashboard.value.suspended_users) +
    numberValue(dashboard.value.disputed) +
    numberValue(dashboard.value.open_tickets) +
    numberValue(dashboard.value.system_health?.overdue_orders),
  );

  const metrics = computed<SuperadminMetric[]>(() => [
    {
      label: "Active tenants",
      value: String(crossTenant.value.summary?.active_tenants ?? activeTenants.value.length),
      detail: `${inactiveTenants.value.length} inactive or paused tenant(s).`,
      tone: inactiveTenants.value.length ? "warn" : "good",
    },
    {
      label: "Platform revenue",
      value: money(crossTenant.value.summary?.total_revenue ?? dashboard.value.total_revenue),
      detail: `${dashboard.value.failed_payments ?? 0} failed payments across platform.`,
      tone: "good",
    },
    {
      label: "Total users",
      value: String(crossTenant.value.summary?.total_users ?? dashboard.value.total_users ?? 0),
      detail: `${dashboard.value.suspended_users ?? 0} suspended, ${dashboard.value.active_users ?? 0} active.`,
      tone: dashboard.value.suspended_users ? "warn" : "neutral",
    },
    {
      label: "Risk workload",
      value: String(riskCount.value),
      detail: `${pendingAppeals.value.length} pending appeal(s), ${dashboard.value.open_tickets ?? 0} open tickets.`,
      tone: riskCount.value ? "risk" : "neutral",
    },
  ]);

  const filteredUsers = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return users.value.filter((user) =>
      !needle ||
      [user.username, user.email, user.role, user.is_suspended ? "suspended" : "active"]
        .some((value) => String(value).toLowerCase().includes(needle)),
    );
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        const seededTenants = previewTenants();
        tenants.value = seededTenants;
        crossTenant.value = {
          summary: {
            total_tenants: 3,
            active_tenants: 2,
            total_revenue: 1243700,
            total_orders: 956,
            total_users: 2984,
            total_disputes: 13,
            total_tickets: 75,
          },
          tenants: seededTenants,
          top_performers: {
            by_revenue: seededTenants.slice(0, 2),
            by_orders: seededTenants.slice(0, 2),
          },
        };
        dashboard.value = {
          total_users: 2984,
          active_users: 2760,
          suspended_users: 18,
          total_admins: 12,
          total_support: 28,
          total_editors: 41,
          total_writers: 820,
          total_clients: 2083,
          total_revenue: 1243700,
          pending_payouts: 28400,
          failed_payments: 7,
          total_orders: 20580,
          in_progress: 410,
          completed: 19120,
          disputed: 13,
          open_tickets: 75,
          closed_tickets: 1630,
          system_health: {
            orders_last_24h: 64,
            orders_last_7d: 486,
            new_users_last_24h: 21,
            new_users_last_7d: 222,
            overdue_orders: 9,
            unassigned_orders: 31,
          },
          recent_orders: [
            { id: 10001, topic: "Nursing leadership reflection", website: "WritePro Global", status: "in_progress", total_price: 188 },
            { id: 10012, topic: "Marketing analytics case study", website: "EssayDesk", status: "disputed", total_price: 240 },
          ],
        };
        users.value = [
          { id: 11, username: "site.admin", email: "admin@writepro.test", role: "admin", is_suspended: false, is_on_probation: false },
          { id: 102, username: "writer.risk", email: "writer-risk@example.com", role: "writer", is_suspended: true, is_on_probation: true },
          { id: 209, username: "support.lead", email: "support@example.com", role: "support", is_suspended: false, is_on_probation: false },
        ];
        logs.value = [
          { id: 1, action_type: "Tenant Updated", action_details: "Updated SEO settings for WritePro Global", formatted_timestamp: "2026-05-26 05:42:00" },
          { id: 2, action_type: "Appeal Approved", action_details: "Approved suspension appeal for writer.risk", formatted_timestamp: "2026-05-25 18:20:00" },
        ];
        appeals.value = [
          {
            id: 71,
            user_username: "writer.risk",
            user_email: "writer-risk@example.com",
            appeal_type: "suspension",
            status: "pending",
            reason: "Writer submitted evidence that the missed deadline was caused by duplicate assignment.",
            submitted_at: new Date(Date.now() - 1000 * 60 * 60 * 7).toISOString(),
          },
        ];
        selectedUserId.value = users.value[0]?.id ?? null;
        return;
      }

      const [dashboardRes, tenantsRes, comparisonRes, crossTenantRes, usersRes, logsRes, appealsRes] =
        await Promise.allSettled([
          superadminApi.dashboard(),
          superadminApi.tenants(),
          superadminApi.tenantComparison(),
          superadminApi.crossTenantAnalytics(),
          superadminApi.users({ page_size: 50 }),
          superadminApi.logs({ page_size: 20 }),
          superadminApi.appeals({ status: "pending", page_size: 20 }),
        ]);

      if (dashboardRes.status === "fulfilled") dashboard.value = dashboardRes.value.data;
      if (tenantsRes.status === "fulfilled") tenants.value = tenantsRes.value.data.tenants;
      if (comparisonRes.status === "fulfilled" && !tenants.value.length) tenants.value = comparisonRes.value.data.tenants;
      if (crossTenantRes.status === "fulfilled") crossTenant.value = crossTenantRes.value.data;
      if (usersRes.status === "fulfilled") users.value = normalizeList(usersRes.value.data);
      if (logsRes.status === "fulfilled") logs.value = normalizeList(logsRes.value.data);
      if (appealsRes.status === "fulfilled") appeals.value = normalizeList(appealsRes.value.data);
      selectedUserId.value = users.value[0]?.id ?? null;

      const failed = [dashboardRes, tenantsRes, comparisonRes, crossTenantRes, usersRes, logsRes, appealsRes]
        .some((result) => result.status === "rejected");
      if (failed) error.value = "Some superadmin command data is unavailable from the backend.";
    } finally {
      isLoading.value = false;
    }
  }

  async function suspendSelectedUser() {
    if (!selectedUserId.value) return;
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        users.value = users.value.map((user) =>
          user.id === selectedUserId.value ? { ...user, is_suspended: true } : user,
        );
        notice.value = "Preview user suspended.";
        return;
      }
      await superadminApi.suspendUser(selectedUserId.value, reason.value);
      notice.value = "User suspended.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function reactivateSelectedUser() {
    if (!selectedUserId.value) return;
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        users.value = users.value.map((user) =>
          user.id === selectedUserId.value ? { ...user, is_suspended: false } : user,
        );
        notice.value = "Preview user reactivated.";
        return;
      }
      await superadminApi.reactivateUser(selectedUserId.value);
      notice.value = "User reactivated.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function changeSelectedUserRole() {
    if (!selectedUserId.value) return;
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        users.value = users.value.map((user) =>
          user.id === selectedUserId.value ? { ...user, role: roleDraft.value } : user,
        );
        notice.value = "Preview role changed.";
        return;
      }
      await superadminApi.changeUserRole(selectedUserId.value, roleDraft.value);
      notice.value = "User role changed.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function reviewAppeal(appealId: number, decision: "approve" | "reject") {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        appeals.value = appeals.value.map((appeal) =>
          appeal.id === appealId ? { ...appeal, status: decision === "approve" ? "approved" : "rejected" } : appeal,
        );
        notice.value = `Preview appeal ${decision === "approve" ? "approved" : "rejected"}.`;
        return;
      }
      if (decision === "approve") await superadminApi.approveAppeal(appealId);
      else await superadminApi.rejectAppeal(appealId);
      notice.value = `Appeal ${decision === "approve" ? "approved" : "rejected"}.`;
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  return {
    dashboard,
    tenants,
    crossTenant,
    users,
    logs,
    appeals,
    query,
    selectedUserId,
    roleDraft,
    reason,
    isLoading,
    isMutating,
    error,
    notice,
    activeTenants,
    inactiveTenants,
    pendingAppeals,
    riskCount,
    metrics,
    filteredUsers,
    hydrate,
    suspendSelectedUser,
    reactivateSelectedUser,
    changeSelectedUserRole,
    reviewAppeal,
    money,
  };
});
