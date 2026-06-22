import { computed, reactive, ref } from "vue";
import { defineStore } from "pinia";
import { superadminApi } from "@/api/superadmin";
import { useAuthStore } from "@/stores/auth";
import type {
  TenantCreatePayload,
  TenantDetail,
  TenantStaffMember,
  TenantSummary,
  TenantUpdatePayload,
} from "@/types/superadmin";

function previewTenantDetail(summary: TenantSummary): TenantDetail {
  const base = {
    id: summary.id,
    name: summary.name ?? "Unknown",
    domain: summary.domain ?? "",
    slug: (summary.domain ?? "").split(".")[0] ?? "tenant",
    is_active: summary.is_active ?? true,
    is_deleted: false,
    order_count: summary.order_count ?? 0,
    user_count: summary.user_count ?? 0,
    total_revenue: summary.total_revenue ?? 0,
    recent_orders_30d: summary.recent_orders_30d ?? 0,
    new_users_30d: summary.new_users_30d ?? 0,
    avg_order_value: summary.avg_order_value ?? 0,
    metrics: summary.metrics,
    billing_email: `billing@${summary.domain ?? "example.com"}`,
    support_email: `support@${summary.domain ?? "example.com"}`,
    writer_count: Math.floor((summary.user_count ?? 0) * 0.42),
    client_count: Math.floor((summary.user_count ?? 0) * 0.51),
    admin_count: Math.max(1, Math.floor((summary.user_count ?? 0) * 0.01)),
    plan: {
      name: summary.is_active ? "Growth" : "Suspended",
      price_per_month: summary.is_active ? 299 : null,
      features: ["Unlimited orders", "Priority writer pool", "Analytics dashboard", "Custom branding"],
    },
    feature_flags: {
      bidding_enabled: true,
      classes_enabled: [14, 15].includes(summary.id),
      special_orders_enabled: true,
      wallet_enabled: true,
      file_uploads_enabled: true,
      seo_blog_enabled: true,
    },
    allowed_subjects: ["Essays", "Research Papers", "Business Reports", "Dissertations", "Case Studies"],
    staff: [
      {
        id: 1,
        user_id: 11 + summary.id,
        username: `admin.${(summary.slug ?? summary.domain ?? "site").split(".")[0]}`,
        email: `admin@${summary.domain ?? "example.com"}`,
        role: "admin",
        joined_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 180).toISOString(),
      },
      {
        id: 2,
        user_id: 21 + summary.id,
        username: `support.${(summary.slug ?? summary.domain ?? "site").split(".")[0]}`,
        email: `support@${summary.domain ?? "example.com"}`,
        role: "support",
        joined_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 90).toISOString(),
      },
    ] as TenantStaffMember[],
    recent_orders: [
      { id: 9000 + summary.id * 10, topic: "Reflective nursing essay", status: "completed", total_price: 160 },
      { id: 9001 + summary.id * 10, topic: "Marketing analytics case study", status: "in_progress", total_price: 220 },
      { id: 9002 + summary.id * 10, topic: "Literature review on AI ethics", status: "pending", total_price: 180 },
    ],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 365).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    suspended_at: summary.is_active ? null : new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
    suspension_reason: summary.is_active ? null : "Billing delinquency — awaiting payment confirmation.",
  };
  return base;
}

const PREVIEW_SUMMARIES: TenantSummary[] = [
  {
    id: 14,
    name: "NurseMyGrade",
    domain: "nursemygrade.com",
    slug: "nursemygrade",
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
    id: 15,
    name: "EssayManiacs",
    domain: "essaymaniacs.com",
    slug: "essaymaniacs",
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
    id: 10,
    name: "GradeCrest",
    domain: "gradecrest.com",
    slug: "gradecrest",
    is_active: true,
    user_count: 760,
    order_count: 4810,
    total_revenue: 298700,
    recent_orders_30d: 214,
    new_users_30d: 53,
    avg_order_value: 112,
    metrics: {
      users: { total: 760, new_this_period: 53 },
      orders: { total: 214, completed: 191, completion_rate: 89.3 },
      revenue: { total: 298700, avg_per_order: 112 },
      disputes: { total: 3, resolution_rate: 100 },
      support: { total_tickets: 18, resolution_rate: 94.4 },
    },
  },
  {
    id: 7,
    name: "ResearchPaperMate",
    domain: "researchpapermate.com",
    slug: "researchpapermate",
    is_active: true,
    user_count: 410,
    order_count: 2340,
    total_revenue: 159600,
    recent_orders_30d: 98,
    new_users_30d: 27,
    avg_order_value: 134,
    metrics: {
      users: { total: 410, new_this_period: 27 },
      orders: { total: 98, completed: 86, completion_rate: 87.8 },
      revenue: { total: 159600, avg_per_order: 134 },
      disputes: { total: 2, resolution_rate: 100 },
      support: { total_tickets: 11, resolution_rate: 90.9 },
    },
  },
];

export const useTenantsStore = defineStore("tenants", () => {
  const list = ref<TenantSummary[]>([]);
  const detail = ref<TenantDetail | null>(null);
  const isLoading = ref(false);
  const isLoadingDetail = ref(false);
  const isSaving = ref(false);
  const error = ref("");
  const notice = ref("");
  const query = ref("");
  const statusFilter = ref<"all" | "active" | "inactive">("all");

  const createForm = reactive<TenantCreatePayload>({
    name: "",
    domain: "",
    slug: "",
    billing_email: "",
    support_email: "",
    plan_name: "Growth",
  });

  const editForm = reactive<TenantUpdatePayload>({});

  const showCreateModal = ref(false);

  const filtered = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return list.value.filter((t) => {
      if (statusFilter.value === "active" && t.is_active === false) return false;
      if (statusFilter.value === "inactive" && t.is_active !== false) return false;
      if (!needle) return true;
      return [t.name, t.domain, t.slug].some((v) => String(v ?? "").toLowerCase().includes(needle));
    });
  });

  const activeTenants = computed(() => list.value.filter((t) => t.is_active !== false));
  const inactiveTenants = computed(() => list.value.filter((t) => t.is_active === false));

  function money(value: unknown): string {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
      Number(value ?? 0),
    );
  }

  async function loadList() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        list.value = PREVIEW_SUMMARIES;
        return;
      }
      const { data } = await superadminApi.tenants();
      list.value = data.tenants ?? [];
    } catch {
      error.value = "Unable to load tenants.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadDetail(id: number | string) {
    const auth = useAuthStore();
    isLoadingDetail.value = true;
    error.value = "";
    detail.value = null;
    try {
      if (auth.isPreviewSession) {
        const summary = PREVIEW_SUMMARIES.find((t) => String(t.id) === String(id)) ?? PREVIEW_SUMMARIES[0];
        detail.value = previewTenantDetail(summary);
        return;
      }
      const { data } = await superadminApi.getTenant(id);
      detail.value = data;
    } catch {
      error.value = "Unable to load tenant details.";
    } finally {
      isLoadingDetail.value = false;
    }
  }

  async function createTenant() {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const newTenant: TenantSummary = {
          id: Date.now(),
          name: createForm.name,
          domain: createForm.domain,
          slug: createForm.slug,
          is_active: true,
          user_count: 0,
          order_count: 0,
          total_revenue: 0,
        };
        list.value = [newTenant, ...list.value];
        notice.value = "Preview tenant created.";
        showCreateModal.value = false;
        resetCreateForm();
        return newTenant;
      }
      const { data } = await superadminApi.createTenant({ ...createForm });
      list.value = [data, ...list.value];
      notice.value = "Tenant created.";
      showCreateModal.value = false;
      resetCreateForm();
      return data;
    } catch {
      error.value = "Unable to create tenant.";
    } finally {
      isSaving.value = false;
    }
  }

  async function updateTenant(id: number | string, payload: TenantUpdatePayload) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (detail.value && String(detail.value.id) === String(id)) {
          detail.value = { ...detail.value, ...payload };
        }
        notice.value = "Preview tenant updated.";
        return detail.value;
      }
      const { data } = await superadminApi.updateTenant(id, payload);
      detail.value = data;
      notice.value = "Tenant updated.";
      return data;
    } catch {
      error.value = "Unable to update tenant.";
    } finally {
      isSaving.value = false;
    }
  }

  async function suspendTenant(id: number | string, reason?: string) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (detail.value && String(detail.value.id) === String(id)) {
          detail.value = {
            ...detail.value,
            is_active: false,
            suspended_at: new Date().toISOString(),
            suspension_reason: reason ?? null,
          };
        }
        list.value = list.value.map((t) =>
          String(t.id) === String(id) ? { ...t, is_active: false } : t,
        );
        notice.value = "Preview tenant suspended.";
        return;
      }
      const { data } = await superadminApi.suspendTenant(id, reason);
      detail.value = data;
      list.value = list.value.map((t) => (String(t.id) === String(id) ? { ...t, is_active: false } : t));
      notice.value = "Tenant suspended.";
    } catch {
      error.value = "Unable to suspend tenant.";
    } finally {
      isSaving.value = false;
    }
  }

  async function activateTenant(id: number | string) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (detail.value && String(detail.value.id) === String(id)) {
          detail.value = { ...detail.value, is_active: true, suspended_at: null, suspension_reason: null };
        }
        list.value = list.value.map((t) => (String(t.id) === String(id) ? { ...t, is_active: true } : t));
        notice.value = "Preview tenant activated.";
        return;
      }
      const { data } = await superadminApi.activateTenant(id);
      detail.value = data;
      list.value = list.value.map((t) => (String(t.id) === String(id) ? { ...t, is_active: true } : t));
      notice.value = "Tenant activated.";
    } catch {
      error.value = "Unable to activate tenant.";
    } finally {
      isSaving.value = false;
    }
  }

  async function removeStaff(tenantId: number | string, staffId: number) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (detail.value) {
          detail.value = {
            ...detail.value,
            staff: detail.value.staff.filter((s) => s.id !== staffId),
          };
        }
        notice.value = "Preview staff member removed.";
        return;
      }
      await superadminApi.removeTenantStaff(tenantId, staffId);
      if (detail.value) {
        detail.value = {
          ...detail.value,
          staff: detail.value.staff.filter((s) => s.id !== staffId),
        };
      }
      notice.value = "Staff member removed.";
    } catch {
      error.value = "Unable to remove staff member.";
    } finally {
      isSaving.value = false;
    }
  }

  function resetCreateForm() {
    createForm.name = "";
    createForm.domain = "";
    createForm.slug = "";
    createForm.billing_email = "";
    createForm.support_email = "";
    createForm.plan_name = "Growth";
  }

  function openCreateModal() {
    resetCreateForm();
    showCreateModal.value = true;
  }

  return {
    list,
    detail,
    isLoading,
    isLoadingDetail,
    isSaving,
    error,
    notice,
    query,
    statusFilter,
    createForm,
    editForm,
    showCreateModal,
    filtered,
    activeTenants,
    inactiveTenants,
    money,
    loadList,
    loadDetail,
    createTenant,
    updateTenant,
    suspendTenant,
    activateTenant,
    removeStaff,
    openCreateModal,
  };
});
