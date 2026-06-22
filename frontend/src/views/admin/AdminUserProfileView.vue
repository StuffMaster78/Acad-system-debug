<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Activity,
  ArrowLeft,
  Ban,
  CheckCircle2,
  ClipboardCopy,
  CreditCard,
  KeyRound,
  Link,
  LogOut,
  Package,
  RefreshCw,
  ShieldCheck,
  ShieldOff,
  Sparkles,
  BookOpen,
  UserCog,
  Wallet,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useAdminAccessStore } from "@/stores/adminAccess";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import { api, apiPath } from "@/api/client";
import { authApi, type AdminMagicLinkResponse, type AdminPasswordResetLinkResponse } from "@/api/auth";
import type { AdminManagedUser } from "@/types/adminAccess";
import type { UserRole } from "@/types/roles";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const access = useAdminAccessStore();
const ui = useUiStore();

const userId = computed(() => Number(route.params.id));
const routePrefix = computed(() => route.path.startsWith("/superadmin") ? "/superadmin" : "/admin");
const isSuperadmin = computed(() => auth.role === "superadmin");

const user = ref<AdminManagedUser | null>(null);
const summary = ref<Record<string, any> | null>(null);
const loading = ref(false);
const summaryLoading = ref(false);
const error = ref("");
const notice = ref("");
const activeTab = ref<"overview" | "orders" | "special" | "classes" | "payments" | "activity" | "profile-requests">("overview");

const newRole = ref<UserRole>("support");
const reason = ref("Admin support review from access console.");

const isMutating = ref(false);

// Link generation state
const generatedMagicLink = ref<AdminMagicLinkResponse | null>(null);
const generatedResetLink = ref<AdminPasswordResetLinkResponse | null>(null);
const linkGenerating = ref<"magic" | "reset" | null>(null);
const linkError = ref("");

async function generateMagicLink() {
  if (!user.value) return;
  linkGenerating.value = "magic";
  linkError.value = "";
  generatedMagicLink.value = null;
  try {
    if (auth.isPreviewSession) {
      generatedMagicLink.value = {
        success: true,
        user_id: user.value.id,
        magic_url: `${window.location.origin}/auth/magic-link?token=preview-token-abc123`,
        expires_minutes: 15,
      };
      return;
    }
    const { data } = await authApi.adminGenerateMagicLink(user.value.id);
    generatedMagicLink.value = data;
    ui.toast("Magic link generated. Share it securely.", "success");
  } catch {
    linkError.value = "Failed to generate magic link.";
  } finally {
    linkGenerating.value = null;
  }
}

async function generateResetLink() {
  if (!user.value) return;
  linkGenerating.value = "reset";
  linkError.value = "";
  generatedResetLink.value = null;
  try {
    if (auth.isPreviewSession) {
      generatedResetLink.value = {
        success: true,
        user_id: user.value.id,
        reset_link: `${window.location.origin}/auth/reset-password?token=preview-reset-abc123`,
        otp_code: "482910",
        token: "preview-reset-abc123",
        expires_hours: 24,
      };
      return;
    }
    const { data } = await authApi.adminGeneratePasswordResetLink(user.value.id);
    generatedResetLink.value = data;
    ui.toast("Password reset link generated.", "success");
  } catch {
    linkError.value = "Failed to generate password reset link.";
  } finally {
    linkGenerating.value = null;
  }
}

function copyToClipboard(text: string, label = "Copied") {
  navigator.clipboard.writeText(text).then(() => ui.toast(`${label} copied to clipboard.`, "success"));
}

const roleOptions = computed<UserRole[]>(() => {
  const base: UserRole[] = ["client", "writer", "editor", "support", "admin"];
  if (isSuperadmin.value) base.push("superadmin");
  return base;
});

function statusTone(u: AdminManagedUser) {
  if (u.is_blacklisted) return "danger";
  if (u.is_suspended) return "danger";
  if (!u.is_active) return "warning";
  return "success";
}

function statusLabel(u: AdminManagedUser) {
  if (u.is_blacklisted) return "blacklisted";
  if (u.is_suspended) return "suspended";
  if (!u.is_active) return "inactive";
  return "active";
}

function roleTone(role?: string | null) {
  if (role === "superadmin") return "danger";
  if (role === "admin") return "warning";
  if (role === "support" || role === "editor") return "neutral";
  return "success";
}

function fmt(v?: string | null) { return v || "—"; }
function fmtDate(v?: string | null) {
  if (!v) return "Never";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(v));
}
function money(v?: string | number | null) {
  if (v == null || v === "") return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(v));
}

async function loadUser() {
  loading.value = true;
  error.value = "";
  try {
    if (auth.isPreviewSession) {
      user.value = access.users.find((u) => u.id === userId.value) ?? null;
      if (!user.value) {
        user.value = {
          id: userId.value,
          username: "preview.user",
          email: "preview@example.com",
          full_name: "Preview User",
          role: "client",
          role_display: "Client",
          is_active: true,
          is_suspended: false,
          is_blacklisted: false,
          is_on_probation: false,
          website: { id: 1, name: "NurseMyGrade", domain: "nursemygrade.com" },
          date_joined: new Date(Date.now() - 1000 * 60 * 60 * 24 * 200).toISOString(),
          last_login: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        };
      }
      return;
    }
    const { data } = await api.get<AdminManagedUser>(apiPath(`/admin-management/user-management/${userId.value}/`));
    user.value = data;
    if (user.value) {
      newRole.value = user.value.role as UserRole;
    }
  } catch {
    error.value = "Could not load user profile.";
  } finally {
    loading.value = false;
  }
}

async function loadSummary() {
  summaryLoading.value = true;
  try {
    if (auth.isPreviewSession) {
      summary.value = {
        orders_as_client: {
          total: 14,
          active: 3,
          completed: 10,
          total_spend: "1420.00",
          recent: [
            { id: 1001, reference: "ORD-1001", status: "completed", total_price: "120.00", created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString() },
            { id: 1002, reference: "ORD-1002", status: "in_progress", total_price: "250.00", created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString() },
          ],
        },
        orders_as_writer: { total: 0, active: 0, completed: 0, total_earned: "0", recent: [] },
        special_orders: { total: 2, active: 1 },
        class_orders: { total: 1, active: 1 },
        wallets: [{ wallet_type: "client", available_balance: "85.50", pending_balance: "0.00", currency: "USD" }],
        audit_log: [
          { action: "login", details: "Successful login from 192.168.1.1", ip_address: "192.168.1.1", created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
          { action: "order_created", details: "Created order ORD-1002", ip_address: "192.168.1.1", created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString() },
        ],
      };
      return;
    }
    const { data } = await api.get(apiPath(`/admin-management/user-management/${userId.value}/summary/`));
    summary.value = data;
  } catch {
    // summary is optional — don't show error
  } finally {
    summaryLoading.value = false;
  }
}

async function doAction(action: "suspend" | "unsuspend" | "unlock" | "kickout" | "reset" | "promote") {
  if (!user.value) return;
  isMutating.value = true;
  notice.value = "";
  error.value = "";
  try {
    if (auth.isPreviewSession) {
      if (action === "suspend") user.value = { ...user.value, is_suspended: true, is_active: false };
      if (action === "unsuspend" || action === "unlock") user.value = { ...user.value, is_suspended: false, is_active: true };
      if (action === "promote") user.value = { ...user.value, role: "admin", role_display: "Admin" };
      notice.value = `Preview: ${action} applied to ${user.value.email}.`;
      ui.toast(notice.value, "success");
      return;
    }
    if (action === "suspend") await api.post(apiPath(`/admin-management/user-management/${userId.value}/suspend/`), { reason: reason.value, duration_days: 30 });
    if (action === "unsuspend") await api.post(apiPath(`/admin-management/user-management/${userId.value}/unsuspend/`), { reason: reason.value });
    if (action === "unlock") await api.post(apiPath(`/auth/admin/users/${userId.value}/unlock/`), {});
    if (action === "kickout") await api.post(apiPath(`/auth/admin/users/${userId.value}/kickout/`), { reason: reason.value });
    if (action === "reset") await api.post(apiPath(`/admin-management/user-management/${userId.value}/reset_password/`), {});
    if (action === "promote") await api.post(apiPath(`/admin-management/user-management/${userId.value}/promote_to_admin/`), {});
    notice.value = `${action} completed for ${user.value.email}.`;
    ui.toast(notice.value, "success");
    await loadUser();
  } catch {
    error.value = `Failed to ${action} user.`;
    ui.toast(error.value, "error");
  } finally {
    isMutating.value = false;
  }
}

async function doChangeRole() {
  if (!user.value) return;
  isMutating.value = true;
  notice.value = "";
  error.value = "";
  try {
    if (auth.isPreviewSession) {
      user.value = { ...user.value, role: newRole.value, role_display: newRole.value };
      notice.value = `Preview: role changed to ${newRole.value}.`;
      ui.toast(notice.value, "success");
      return;
    }
    await api.post(apiPath(`/admin-management/user-management/${userId.value}/change_role/`), { role: newRole.value });
    notice.value = `Role changed to ${newRole.value}.`;
    ui.toast(notice.value, "success");
    await loadUser();
  } catch {
    error.value = "Failed to change role.";
    ui.toast(error.value, "error");
  } finally {
    isMutating.value = false;
  }
}

async function doDeleteUser() {
  if (!user.value || !isSuperadmin.value) return;
  if (!window.confirm(`Delete account for ${user.value.email}? This cannot be undone.`)) return;
  isMutating.value = true;
  try {
    if (auth.isPreviewSession) {
      ui.toast("Preview: account would be deleted.", "info");
      return;
    }
    await api.delete(apiPath(`/admin-management/user-management/${userId.value}/`));
    ui.toast("Account deleted.", "success");
    router.push(`${routePrefix.value}/access`);
  } catch {
    ui.toast("Failed to delete account.", "error");
  } finally {
    isMutating.value = false;
  }
}

function writerProfileRoute() {
  if (!user.value) return null;
  if (user.value.role !== "writer") return null;
  const regId = user.value.writer_profile?.registration_id;
  if (!regId) return null;
  return `${routePrefix.value}/writers/${regId}`;
}

function clientProfileRoute() {
  if (!user.value) return null;
  if (user.value.role !== "client") return null;
  const profileId = user.value.client_profile?.id;
  if (!profileId) return null;
  return `${routePrefix.value}/clients/${profileId}`;
}

const tabs = [
  { key: "overview", label: "Overview", icon: UserCog },
  { key: "orders", label: "Orders", icon: Package },
  { key: "special", label: "Special Orders", icon: Sparkles },
  { key: "classes", label: "Classes", icon: BookOpen },
  { key: "payments", label: "Payments & Wallet", icon: Wallet },
  { key: "activity", label: "Activity", icon: Activity },
  { key: "profile-requests", label: "Profile Requests", icon: ClipboardCopy },
] as const;

const profileUpdateRequests = ref<import("@/types/adminAccess").ProfileUpdateRequestRecord[]>([]);

async function loadProfileRequests() {
  try {
    const res = await api.get<{ results?: unknown[]; [key: string]: unknown }>(
      apiPath(`/client-management/profile-update-requests/admin/?user=${userId.value}`)
    );
    const data = res.data;
    profileUpdateRequests.value = (Array.isArray(data) ? data : (data.results ?? [])) as import("@/types/adminAccess").ProfileUpdateRequestRecord[];
  } catch {
    // Non-critical; swallow silently
  }
}

onMounted(async () => {
  await loadUser();
  loadSummary();
  loadProfileRequests();
});
</script>

<template>
  <div class="space-y-6">

    <!-- Back nav -->
    <button
      class="focus-ring inline-flex items-center gap-2 text-sm font-semibold text-graphite hover:text-ink"
      type="button"
      @click="router.push(`${routePrefix}/access`)"
    >
      <ArrowLeft class="h-4 w-4" /> Back to user directory
    </button>

    <!-- Loading -->
    <div v-if="loading" class="py-20">
      <LoadingSpinner label="Loading user profile…" />
    </div>

    <template v-else-if="user">

      <!-- User header -->
      <section class="overflow-hidden rounded-md border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 p-6 md:flex-row md:items-start md:justify-between">
          <div class="flex items-start gap-4">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-slate-100 text-2xl font-bold text-graphite">
              {{ (user.full_name || user.username).charAt(0).toUpperCase() }}
            </div>
            <div>
              <h1 class="text-2xl font-bold text-ink">{{ user.full_name || user.username }}</h1>
              <p class="mt-0.5 text-sm text-graphite">{{ user.email }}</p>
              <p class="mt-0.5 text-xs text-slate-400">@{{ user.username }} · #{{ user.id }}</p>
              <div class="mt-2 flex flex-wrap gap-2">
                <StatusPill :label="user.role_display || user.role" :tone="roleTone(user.role)" />
                <StatusPill :label="statusLabel(user)" :tone="statusTone(user)" />
                <StatusPill v-if="user.is_on_probation" label="probation" tone="warning" />
              </div>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-if="writerProfileRoute()"
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold hover:border-signal hover:text-signal"
              type="button"
              @click="router.push(writerProfileRoute()!)"
            >
              Writer profile
            </button>
            <button
              v-if="clientProfileRoute()"
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold hover:border-signal hover:text-signal"
              type="button"
              @click="router.push(clientProfileRoute()!)"
            >
              Client profile
            </button>
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold"
              type="button"
              :disabled="loading"
              @click="loadUser(); loadSummary();"
            >
              <RefreshCw class="h-4 w-4" /> Refresh
            </button>
          </div>
        </div>

        <!-- Quick info strip -->
        <dl class="grid gap-px bg-slate-100 sm:grid-cols-5">
          <div class="bg-white px-5 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Joined</dt>
            <dd class="mt-1 text-sm text-ink">{{ fmtDate(user.date_joined) }}</dd>
          </div>
          <div class="bg-white px-5 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Last login</dt>
            <dd class="mt-1 text-sm text-ink">{{ fmtDate(user.last_login) }}</dd>
          </div>
          <div class="bg-white px-5 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Phone</dt>
            <dd class="mt-1 text-sm text-ink">{{ user.phone_number || '—' }}</dd>
          </div>
          <div class="bg-white px-5 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Website</dt>
            <dd class="mt-1 text-sm text-ink">{{ user.website?.name || '—' }}</dd>
            <dd class="text-xs text-graphite">{{ user.website?.domain || '' }}</dd>
          </div>
          <div class="bg-white px-5 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Account status</dt>
            <dd class="mt-1">
              <StatusPill :label="statusLabel(user)" :tone="statusTone(user)" />
            </dd>
          </div>
        </dl>
      </section>

      <!-- Notice / error banner -->
      <p v-if="notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ notice }}</p>
      <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</p>

      <!-- Main content: tabs + actions sidebar -->
      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">

        <!-- LEFT: Tabs -->
        <div class="space-y-4">
          <!-- Tab bar -->
          <nav class="flex gap-1 overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="focus-ring flex shrink-0 items-center gap-1.5 rounded px-3 py-2 text-xs font-semibold"
              :class="activeTab === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="activeTab = tab.key"
            >
              <component :is="tab.icon" class="h-3.5 w-3.5" />
              {{ tab.label }}
            </button>
          </nav>

          <!-- Overview tab -->
          <template v-if="activeTab === 'overview'">
            <div v-if="summaryLoading" class="py-8 text-center text-sm text-graphite animate-pulse">Loading summary…</div>
            <div v-else-if="summary" class="space-y-4">
              <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div class="rounded-md border border-slate-200 bg-white p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Orders (as client)</p>
                  <p class="mt-2 text-3xl font-bold text-ink">{{ summary.orders_as_client?.total ?? 0 }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ summary.orders_as_client?.active ?? 0 }} active · {{ summary.orders_as_client?.completed ?? 0 }} completed</p>
                </div>
                <div class="rounded-md border border-slate-200 bg-white p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Total spend</p>
                  <p class="mt-2 min-w-0 truncate text-xl font-bold text-ink" :title="money(summary.orders_as_client?.total_spend)">
                    {{ money(summary.orders_as_client?.total_spend) }}
                  </p>
                  <p class="mt-1 text-xs text-graphite">Across all orders</p>
                </div>
                <div class="rounded-md border border-slate-200 bg-white p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Special orders</p>
                  <p class="mt-2 text-3xl font-bold text-ink">{{ summary.special_orders?.total ?? 0 }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ summary.special_orders?.active ?? 0 }} active</p>
                </div>
                <div class="rounded-md border border-slate-200 bg-white p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Classes</p>
                  <p class="mt-2 text-3xl font-bold text-ink">{{ summary.class_orders?.total ?? 0 }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ summary.class_orders?.active ?? 0 }} active</p>
                </div>
              </div>

              <!-- Writer stats (if applicable) -->
              <div v-if="user.role === 'writer' && summary.orders_as_writer?.total" class="grid gap-4 sm:grid-cols-3">
                <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Orders completed (writer)</p>
                  <p class="mt-2 text-3xl font-bold text-ink">{{ summary.orders_as_writer.completed }}</p>
                </div>
                <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Total earned</p>
                  <p class="mt-2 min-w-0 truncate text-xl font-bold text-ink" :title="money(summary.orders_as_writer.total_earned)">
                    {{ money(summary.orders_as_writer.total_earned) }}
                  </p>
                </div>
                <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4">
                  <p class="text-xs font-semibold uppercase text-graphite">Active assignments</p>
                  <p class="mt-2 text-3xl font-bold text-ink">{{ summary.orders_as_writer.active }}</p>
                </div>
              </div>

              <!-- Wallet balances -->
              <div v-if="summary.wallets?.length" class="rounded-md border border-slate-200 bg-white p-4">
                <h3 class="mb-3 text-sm font-semibold text-ink">Wallet balances</h3>
                <div class="grid gap-3 sm:grid-cols-2">
                  <div
                    v-for="wallet in summary.wallets"
                    :key="wallet.wallet_type"
                    class="flex items-center gap-3 rounded-md border border-slate-200 bg-slate-50 p-3"
                  >
                    <Wallet class="h-5 w-5 shrink-0 text-graphite" />
                    <div>
                      <p class="text-xs font-semibold uppercase text-graphite">{{ wallet.wallet_type }}</p>
                      <p class="mt-0.5 text-base font-bold text-ink">{{ money(wallet.available_balance) }} <span class="text-xs text-graphite">{{ wallet.currency }}</span></p>
                      <p v-if="Number(wallet.pending_balance) > 0" class="text-xs text-amber-600">+{{ money(wallet.pending_balance) }} pending</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent orders -->
              <div v-if="summary.orders_as_client?.recent?.length" class="rounded-md border border-slate-200 bg-white overflow-hidden">
                <div class="border-b border-slate-200 px-4 py-3">
                  <h3 class="text-sm font-semibold text-ink">Recent orders</h3>
                </div>
                <table class="min-w-full text-sm">
                  <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
                    <tr>
                      <th class="px-4 py-2 text-left">Reference</th>
                      <th class="px-4 py-2 text-left">Status</th>
                      <th class="px-4 py-2 text-right">Amount</th>
                      <th class="px-4 py-2 text-right">Date</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="order in summary.orders_as_client.recent" :key="order.id">
                      <td class="px-4 py-2 font-mono text-xs">{{ order.reference }}</td>
                      <td class="px-4 py-2"><StatusPill :label="order.status" :tone="order.status === 'completed' ? 'success' : order.status === 'cancelled' ? 'danger' : 'neutral'" /></td>
                      <td class="px-4 py-2 text-right font-semibold">{{ money(order.total_price) }}</td>
                      <td class="px-4 py-2 text-right text-graphite">{{ fmtDate(order.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-graphite">
              Summary data not available for this user.
            </div>
          </template>

          <!-- Orders tab -->
          <template v-else-if="activeTab === 'orders'">
            <div class="rounded-md border border-slate-200 bg-white p-6">
              <div class="flex items-center gap-3 mb-4">
                <Package class="h-5 w-5 text-signal" />
                <h3 class="font-semibold text-ink">Orders</h3>
              </div>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-signal px-3 py-2 text-sm font-semibold text-signal"
                type="button"
                @click="router.push(`${routePrefix}/orders?client=${user.id}`)"
              >
                View all orders for this user
              </button>
            </div>
          </template>

          <!-- Special Orders tab -->
          <template v-else-if="activeTab === 'special'">
            <div class="rounded-md border border-slate-200 bg-white p-6">
              <div class="flex items-center gap-3 mb-4">
                <Sparkles class="h-5 w-5 text-signal" />
                <h3 class="font-semibold text-ink">Special Orders</h3>
              </div>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-signal px-3 py-2 text-sm font-semibold text-signal"
                type="button"
                @click="router.push(`${routePrefix}/special-orders?client=${user.id}`)"
              >
                View special orders for this user
              </button>
            </div>
          </template>

          <!-- Classes tab -->
          <template v-else-if="activeTab === 'classes'">
            <div class="rounded-md border border-slate-200 bg-white p-6">
              <div class="flex items-center gap-3 mb-4">
                <BookOpen class="h-5 w-5 text-signal" />
                <h3 class="font-semibold text-ink">Classes</h3>
              </div>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-signal px-3 py-2 text-sm font-semibold text-signal"
                type="button"
                @click="router.push(`${routePrefix}/classes?client=${user.id}`)"
              >
                View class orders for this user
              </button>
            </div>
          </template>

          <!-- Payments & Wallet tab -->
          <template v-else-if="activeTab === 'payments'">
            <div class="space-y-4">
              <div v-if="summary?.wallets?.length" class="rounded-md border border-slate-200 bg-white p-4">
                <h3 class="mb-3 text-sm font-semibold text-ink">Wallet balances</h3>
                <div class="space-y-2">
                  <div
                    v-for="wallet in summary.wallets"
                    :key="wallet.wallet_type"
                    class="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 p-3"
                  >
                    <div>
                      <p class="text-xs font-semibold uppercase text-graphite">{{ wallet.wallet_type }} wallet</p>
                      <p class="mt-0.5 text-xs text-graphite">{{ wallet.currency }}</p>
                    </div>
                    <div class="text-right">
                      <p class="font-bold text-ink">{{ money(wallet.available_balance) }}</p>
                      <p v-if="Number(wallet.pending_balance) > 0" class="text-xs text-amber-600">+{{ money(wallet.pending_balance) }} pending</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="rounded-md border border-slate-200 bg-white p-6">
                <div class="flex items-center gap-3 mb-4">
                  <CreditCard class="h-5 w-5 text-signal" />
                  <h3 class="font-semibold text-ink">Payment history</h3>
                </div>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-signal px-3 py-2 text-sm font-semibold text-signal"
                  type="button"
                  @click="router.push(`${routePrefix}/payments?user=${user.id}`)"
                >
                  View payments for this user
                </button>
              </div>
            </div>
          </template>

          <!-- Activity tab -->
          <template v-else-if="activeTab === 'activity'">
            <div v-if="summaryLoading" class="py-8 text-center text-sm text-graphite animate-pulse">Loading activity…</div>
            <div v-else class="rounded-md border border-slate-200 bg-white overflow-hidden">
              <div class="border-b border-slate-200 px-4 py-3">
                <h3 class="text-sm font-semibold text-ink">Recent activity</h3>
              </div>
              <div v-if="summary?.audit_log?.length" class="divide-y divide-slate-100">
                <div v-for="(entry, i) in summary.audit_log" :key="i" class="px-4 py-3">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-sm font-semibold text-ink capitalize">{{ String(entry.action).replace(/_/g, " ") }}</p>
                      <p v-if="entry.details" class="mt-0.5 text-xs text-graphite">{{ entry.details }}</p>
                      <p v-if="entry.ip_address" class="mt-0.5 text-xs text-slate-400">IP: {{ entry.ip_address }}</p>
                    </div>
                    <time class="shrink-0 text-xs text-slate-400">{{ fmtDate(entry.created_at) }}</time>
                  </div>
                </div>
              </div>
              <div v-else class="px-4 py-10 text-center text-sm text-graphite">
                No activity recorded for this user.
              </div>
            </div>
          </template>

          <!-- Profile Requests tab -->
          <template v-else-if="activeTab === 'profile-requests'">
            <div v-if="profileUpdateRequests.length === 0" class="rounded-md border border-slate-200 bg-white px-4 py-10 text-center text-sm text-graphite">
              No profile update requests found for this user.
            </div>
            <div v-else class="rounded-md border border-slate-200 bg-white overflow-hidden">
              <div class="border-b border-slate-200 px-4 py-3">
                <h3 class="text-sm font-semibold text-ink">Profile update requests ({{ profileUpdateRequests.length }})</h3>
              </div>
              <div class="divide-y divide-slate-100">
                <div v-for="req in profileUpdateRequests" :key="req.id" class="px-4 py-4">
                  <div class="flex items-start justify-between gap-3">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <StatusPill :label="req.status ?? 'unknown'" :tone="req.status === 'approved' ? 'success' : req.status === 'rejected' ? 'danger' : 'neutral'" />
                        <time class="text-xs text-slate-400">{{ fmtDate(req.created_at) }}</time>
                      </div>
                      <div class="mt-2 rounded-md bg-slate-50 px-3 py-2 text-xs text-ink">
                        <template v-for="(val, key) in (req.requested_changes ?? req.changes ?? {})" :key="key">
                          <div class="flex gap-2 py-0.5">
                            <span class="font-semibold text-graphite capitalize">{{ String(key).replace(/_/g, ' ') }}:</span>
                            <span>{{ val }}</span>
                          </div>
                        </template>
                      </div>
                      <p v-if="req.reason" class="mt-1 text-xs text-graphite">Reason: {{ req.reason }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- RIGHT: Actions sidebar -->
        <aside class="space-y-4">

          <!-- Contact info -->
          <section class="rounded-md border border-slate-200 bg-white">
            <div class="border-b border-slate-200 px-4 py-3">
              <h2 class="text-sm font-semibold text-ink">Contact information</h2>
            </div>
            <dl class="divide-y divide-slate-100 px-4">
              <div class="flex items-start gap-3 py-3">
                <Mail class="mt-0.5 h-4 w-4 shrink-0 text-graphite" />
                <div class="min-w-0">
                  <dt class="text-xs font-semibold uppercase text-graphite">Email</dt>
                  <dd class="mt-0.5 break-all text-sm text-ink">{{ user.email }}</dd>
                </div>
              </div>
              <div class="flex items-start gap-3 py-3">
                <KeyRound class="mt-0.5 h-4 w-4 shrink-0 text-graphite" />
                <div>
                  <dt class="text-xs font-semibold uppercase text-graphite">Phone</dt>
                  <dd class="mt-0.5 text-sm text-ink">{{ user.phone_number || '—' }}</dd>
                </div>
              </div>
              <div class="flex items-start gap-3 py-3">
                <ShieldCheck class="mt-0.5 h-4 w-4 shrink-0 text-graphite" />
                <div>
                  <dt class="text-xs font-semibold uppercase text-graphite">Username</dt>
                  <dd class="mt-0.5 text-sm font-mono text-ink">@{{ user.username }}</dd>
                </div>
              </div>
              <div v-if="user.website" class="flex items-start gap-3 py-3">
                <Link class="mt-0.5 h-4 w-4 shrink-0 text-graphite" />
                <div>
                  <dt class="text-xs font-semibold uppercase text-graphite">Website</dt>
                  <dd class="mt-0.5 text-sm text-ink">{{ user.website.name }}</dd>
                  <dd class="text-xs text-graphite">{{ user.website.domain }}</dd>
                </div>
              </div>
            </dl>
          </section>

          <!-- Account controls -->
          <section class="rounded-md border border-slate-200 bg-white">
            <div class="border-b border-slate-200 px-4 py-4">
              <div class="flex items-center gap-2">
                <UserCog class="h-5 w-5 text-signal" />
                <h2 class="text-base font-semibold">Account controls</h2>
              </div>
            </div>
            <div class="space-y-3 p-4">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Action reason</span>
                <textarea v-model="reason" class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
              </label>
              <div class="grid gap-2 sm:grid-cols-2">
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doAction('suspend')"
                >
                  <ShieldOff class="h-4 w-4" /> Suspend
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-1.5 rounded-md border border-emerald-200 bg-emerald-50 px-3 text-sm font-semibold text-emerald-900 disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doAction('unsuspend')"
                >
                  <CheckCircle2 class="h-4 w-4" /> Unsuspend
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doAction('unlock')"
                >
                  <ShieldCheck class="h-4 w-4" /> Unlock
                </button>
                <button
                  class="focus-ring inline-flex h-10 items-center justify-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doAction('kickout')"
                >
                  <LogOut class="h-4 w-4" /> Kick out
                </button>
                <button
                  class="focus-ring col-span-2 inline-flex h-10 items-center justify-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doAction('reset')"
                >
                  <KeyRound class="h-4 w-4" /> Reset password
                </button>
              </div>

              <!-- Change role -->
              <div class="rounded-md border border-slate-200 p-3">
                <label class="block">
                  <span class="text-xs font-semibold uppercase text-graphite">Change role</span>
                  <select
                    v-model="newRole"
                    class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  >
                    <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
                  </select>
                </label>
                <button
                  class="focus-ring mt-2 inline-flex h-10 w-full items-center justify-center gap-1.5 rounded-md bg-ink px-3 text-sm font-semibold text-white disabled:opacity-60"
                  type="button"
                  :disabled="isMutating"
                  @click="doChangeRole"
                >
                  Apply role change
                </button>
              </div>

              <!-- Promote to admin (superadmin only) -->
              <button
                v-if="isSuperadmin && user.role !== 'admin' && user.role !== 'superadmin'"
                class="focus-ring inline-flex h-10 w-full items-center justify-center gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
                type="button"
                :disabled="isMutating"
                @click="doAction('promote')"
              >
                Promote to admin
              </button>

              <!-- Delete (superadmin only) -->
              <button
                v-if="isSuperadmin"
                class="focus-ring inline-flex h-10 w-full items-center justify-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
                type="button"
                :disabled="isMutating"
                @click="doDeleteUser"
              >
                <Ban class="h-4 w-4" /> Delete account
              </button>
            </div>
          </section>

          <!-- Impersonation -->
          <section class="rounded-md border border-slate-200 bg-white p-4">
            <h2 class="text-sm font-semibold text-ink">Impersonation</h2>
            <p class="mt-1 text-xs text-graphite">Open a support session signed in as this user.</p>
            <div class="mt-3 rounded-md border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900">
              Use only for support, QA, or account rescue.
            </div>
            <button
              class="focus-ring mt-3 inline-flex h-9 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="isMutating"
              @click="access.selectedUserId = user.id; access.createImpersonationToken().catch(() => undefined)"
            >
              Generate token
            </button>
            <input
              v-model="access.generatedToken"
              class="focus-ring mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-xs font-mono"
              placeholder="Token will appear here"
              type="text"
              readonly
            />
            <button
              class="focus-ring mt-2 inline-flex h-9 w-full items-center justify-center rounded-md bg-signal px-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="isMutating || !access.generatedToken"
              @click="access.selectedUserId = user.id; access.startImpersonation().catch(() => undefined)"
            >
              Start session
            </button>
          </section>

          <!-- Support auth links -->
          <section class="rounded-md border border-slate-200 bg-white p-4 space-y-3">
            <div>
              <h2 class="text-sm font-semibold text-ink">Support auth links</h2>
              <p class="mt-1 text-xs text-graphite">
                Generate a one-click login or password reset link to share with the user. Never send these in public channels.
              </p>
            </div>

            <p v-if="linkError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
              {{ linkError }}
            </p>

            <!-- Magic link -->
            <div class="space-y-2">
              <button
                class="focus-ring inline-flex h-9 w-full items-center justify-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                type="button"
                :disabled="linkGenerating !== null"
                @click="generateMagicLink"
              >
                <Link class="h-3.5 w-3.5" />
                {{ linkGenerating === 'magic' ? 'Generating…' : 'Generate magic login link' }}
              </button>
              <div v-if="generatedMagicLink" class="rounded-md border border-slate-200 bg-slate-50 p-2">
                <p class="text-xs font-semibold text-graphite mb-1">
                  Magic link · expires in {{ generatedMagicLink.expires_minutes }} min · single-use
                </p>
                <div class="flex gap-1.5">
                  <input
                    :value="generatedMagicLink.magic_url"
                    class="min-w-0 flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-xs font-mono text-graphite"
                    readonly
                  />
                  <button
                    class="focus-ring shrink-0 rounded border border-slate-200 bg-white px-2 py-1 text-xs font-semibold hover:bg-slate-50"
                    type="button"
                    @click="copyToClipboard(generatedMagicLink!.magic_url, 'Magic link')"
                  >
                    <ClipboardCopy class="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Password reset link -->
            <div class="space-y-2">
              <button
                class="focus-ring inline-flex h-9 w-full items-center justify-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                type="button"
                :disabled="linkGenerating !== null"
                @click="generateResetLink"
              >
                <KeyRound class="h-3.5 w-3.5" />
                {{ linkGenerating === 'reset' ? 'Generating…' : 'Generate password reset link' }}
              </button>
              <div v-if="generatedResetLink" class="rounded-md border border-slate-200 bg-slate-50 p-2 space-y-2">
                <p class="text-xs font-semibold text-graphite">
                  Reset link · expires in {{ generatedResetLink.expires_hours }}h
                </p>
                <div class="flex gap-1.5">
                  <input
                    :value="generatedResetLink.reset_link"
                    class="min-w-0 flex-1 rounded border border-slate-200 bg-white px-2 py-1 text-xs font-mono text-graphite"
                    readonly
                  />
                  <button
                    class="focus-ring shrink-0 rounded border border-slate-200 bg-white px-2 py-1 text-xs font-semibold hover:bg-slate-50"
                    type="button"
                    @click="copyToClipboard(generatedResetLink!.reset_link, 'Reset link')"
                  >
                    <ClipboardCopy class="h-3.5 w-3.5" />
                  </button>
                </div>
                <div class="flex items-center justify-between gap-2 rounded border border-amber-200 bg-amber-50 px-2 py-1.5">
                  <div>
                    <p class="text-xs font-semibold text-amber-900">OTP code</p>
                    <p class="font-mono text-base font-bold tracking-widest text-amber-900">{{ generatedResetLink.otp_code }}</p>
                  </div>
                  <button
                    class="focus-ring shrink-0 rounded border border-amber-300 bg-white px-2 py-1 text-xs font-semibold text-amber-900 hover:bg-amber-50"
                    type="button"
                    @click="copyToClipboard(generatedResetLink!.otp_code, 'OTP code')"
                  >
                    <ClipboardCopy class="h-3.5 w-3.5" />
                  </button>
                </div>
                <p class="text-xs text-graphite">Share the link AND the OTP code with the user. Both are required to set a new password.</p>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </template>

    <!-- Error state -->
    <div v-else-if="error" class="py-16 text-center">
      <p class="text-rose-600">{{ error }}</p>
      <button class="mt-4 text-sm font-semibold text-signal hover:underline" @click="loadUser">Retry</button>
    </div>

  </div>
</template>
