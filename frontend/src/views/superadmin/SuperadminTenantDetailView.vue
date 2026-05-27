<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Globe,
  Mail,
  PauseCircle,
  ShieldCheck,
  Trash2,
  Users,
} from "@lucide/vue";
import { useTenantsStore } from "@/stores/tenants";

const route = useRoute();
const router = useRouter();
const tenants = useTenantsStore();

const activeTab = ref<"overview" | "staff" | "orders" | "finance" | "settings" | "actions">("overview");
const suspendReason = ref("");
const showSuspendConfirm = ref(false);

const tabs = [
  { key: "overview", label: "Overview" },
  { key: "staff", label: "Staff" },
  { key: "orders", label: "Recent orders" },
  { key: "finance", label: "Finance" },
  { key: "settings", label: "Settings" },
  { key: "actions", label: "Actions" },
] as const;

onMounted(() => {
  tenants.loadDetail(route.params.id as string);
});

async function handleSuspend() {
  if (!tenants.detail) return;
  await tenants.suspendTenant(tenants.detail.id, suspendReason.value || undefined);
  showSuspendConfirm.value = false;
  suspendReason.value = "";
}

async function handleActivate() {
  if (!tenants.detail) return;
  await tenants.activateTenant(tenants.detail.id);
}

async function toggleFlag(flagKey: string) {
  if (!tenants.detail) return;
  const current = tenants.detail.feature_flags[flagKey] ?? false;
  await tenants.updateTenant(tenants.detail.id, {
    feature_flags: { ...tenants.detail.feature_flags, [flagKey]: !current },
  });
}

function orderStatusClass(status: string) {
  const map: Record<string, string> = {
    completed: "bg-emerald-50 text-emerald-700",
    in_progress: "bg-blue-50 text-blue-700",
    pending: "bg-amber-50 text-amber-700",
    disputed: "bg-rose-50 text-rose-700",
    cancelled: "bg-slate-100 text-graphite",
  };
  return map[status] ?? "bg-slate-100 text-graphite";
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function flagLabel(key: string) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
</script>

<template>
  <div class="space-y-6">
    <!-- Back + title -->
    <div class="flex items-center gap-3">
      <button
        class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink transition-colors"
        type="button"
        @click="router.push('/superadmin/tenants')"
      >
        <ArrowLeft class="h-4 w-4" />
        Tenants
      </button>
    </div>

    <!-- Loading -->
    <div v-if="tenants.isLoadingDetail" class="space-y-4">
      <div class="h-20 rounded-xl bg-slate-100 animate-pulse" />
      <div class="h-48 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <template v-else-if="tenants.detail">
      <!-- Notice / Error -->
      <p v-if="tenants.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ tenants.notice }}</p>
      <p v-if="tenants.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ tenants.error }}</p>

      <!-- Suspension banner -->
      <div
        v-if="tenants.detail.is_active === false"
        class="flex items-start gap-3 rounded-xl bg-rose-50 border border-rose-200 p-4"
      >
        <AlertTriangle class="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
        <div>
          <p class="text-sm font-semibold text-rose-800">Tenant suspended</p>
          <p v-if="tenants.detail.suspension_reason" class="text-xs text-rose-700 mt-0.5">{{ tenants.detail.suspension_reason }}</p>
          <p v-if="tenants.detail.suspended_at" class="text-xs text-rose-600 mt-0.5">Since {{ formatDate(tenants.detail.suspended_at) }}</p>
        </div>
      </div>

      <!-- Header card -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-xl font-bold text-ink">{{ tenants.detail.name }}</h1>
              <span
                class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
                :class="tenants.detail.is_active !== false ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'"
              >
                <CheckCircle2 v-if="tenants.detail.is_active !== false" class="h-3 w-3" />
                <PauseCircle v-else class="h-3 w-3" />
                {{ tenants.detail.is_active !== false ? "Active" : "Suspended" }}
              </span>
            </div>
            <div class="mt-1 flex items-center gap-3 text-xs text-graphite">
              <span class="flex items-center gap-1"><Globe class="h-3 w-3" />{{ tenants.detail.domain }}</span>
              <span class="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-xs">{{ tenants.detail.slug }}</span>
              <span class="flex items-center gap-1"><ShieldCheck class="h-3 w-3" />{{ tenants.detail.plan.name }}</span>
            </div>
          </div>
        </div>

        <!-- Key metrics -->
        <div class="mt-5 grid grid-cols-4 gap-4 border-t border-slate-100 pt-4">
          <div>
            <p class="text-xs text-graphite">Total revenue</p>
            <p class="text-lg font-bold text-ink">{{ tenants.money(tenants.detail.total_revenue) }}</p>
          </div>
          <div>
            <p class="text-xs text-graphite">All-time orders</p>
            <p class="text-lg font-bold text-ink">{{ (tenants.detail.order_count ?? 0).toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs text-graphite">Total users</p>
            <p class="text-lg font-bold text-ink">{{ (tenants.detail.user_count ?? 0).toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs text-graphite">Avg order value</p>
            <p class="text-lg font-bold text-ink">{{ tenants.money(tenants.detail.avg_order_value) }}</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="flex-1 rounded-lg py-2 text-xs font-semibold transition-colors"
          :class="activeTab === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
          type="button"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Overview tab -->
      <div v-if="activeTab === 'overview'" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <!-- Contact -->
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Contact</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center gap-2">
                <Mail class="h-4 w-4 text-graphite shrink-0" />
                <span class="text-ink">{{ tenants.detail.billing_email ?? "—" }}</span>
                <span class="text-xs text-graphite">(billing)</span>
              </div>
              <div class="flex items-center gap-2">
                <Mail class="h-4 w-4 text-graphite shrink-0" />
                <span class="text-ink">{{ tenants.detail.support_email ?? "—" }}</span>
                <span class="text-xs text-graphite">(support)</span>
              </div>
            </div>
          </div>

          <!-- User breakdown -->
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">User breakdown</p>
            <div class="space-y-1.5">
              <div class="flex justify-between text-sm">
                <span class="text-graphite">Writers</span>
                <span class="font-semibold text-ink">{{ tenants.detail.writer_count }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-graphite">Clients</span>
                <span class="font-semibold text-ink">{{ tenants.detail.client_count }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-graphite">Admins / Staff</span>
                <span class="font-semibold text-ink">{{ tenants.detail.admin_count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Plan -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Billing plan</p>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-bold text-ink">{{ tenants.detail.plan.name }}</p>
              <p class="text-xs text-graphite mt-0.5">
                {{ tenants.detail.plan.price_per_month != null ? `$${tenants.detail.plan.price_per_month}/mo` : "Custom pricing" }}
              </p>
            </div>
          </div>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="feature in tenants.detail.plan.features"
              :key="feature"
              class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-graphite"
            >
              {{ feature }}
            </span>
          </div>
        </div>

        <!-- Metrics -->
        <div v-if="tenants.detail.metrics" class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">30-day metrics</p>
          <div class="grid grid-cols-3 gap-4">
            <div v-if="tenants.detail.metrics.orders">
              <p class="text-xs text-graphite">Orders</p>
              <p class="text-base font-bold text-ink">{{ tenants.detail.metrics.orders.total ?? 0 }}</p>
              <div class="mt-1 h-1 rounded-full bg-slate-100">
                <div
                  class="h-1 rounded-full bg-emerald-500"
                  :style="{ width: `${tenants.detail.metrics.orders.completion_rate ?? 0}%` }"
                />
              </div>
              <p class="text-xs text-graphite mt-0.5">{{ tenants.detail.metrics.orders.completion_rate ?? 0 }}% completion</p>
            </div>
            <div v-if="tenants.detail.metrics.disputes">
              <p class="text-xs text-graphite">Disputes</p>
              <p class="text-base font-bold text-ink">{{ tenants.detail.metrics.disputes.total ?? 0 }}</p>
              <p class="text-xs text-graphite">{{ tenants.detail.metrics.disputes.resolution_rate ?? 0 }}% resolved</p>
            </div>
            <div v-if="tenants.detail.metrics.support">
              <p class="text-xs text-graphite">Support tickets</p>
              <p class="text-base font-bold text-ink">{{ tenants.detail.metrics.support.total_tickets ?? 0 }}</p>
              <p class="text-xs text-graphite">{{ tenants.detail.metrics.support.resolution_rate ?? 0 }}% resolved</p>
            </div>
          </div>
        </div>

        <!-- Created / updated -->
        <div class="flex items-center gap-4 text-xs text-graphite px-1">
          <span>Created {{ formatDate(tenants.detail.created_at) }}</span>
          <span>·</span>
          <span>Updated {{ formatDate(tenants.detail.updated_at) }}</span>
        </div>
      </div>

      <!-- Staff tab -->
      <div v-else-if="activeTab === 'staff'" class="space-y-4">
        <div class="rounded-xl border border-slate-200 bg-white shadow-panel overflow-hidden">
          <div class="border-b border-slate-100 px-5 py-3 flex items-center justify-between">
            <p class="text-sm font-semibold text-ink">Staff members ({{ tenants.detail.staff.length }})</p>
          </div>
          <div v-if="!tenants.detail.staff.length" class="flex flex-col items-center gap-2 py-12">
            <Users class="h-7 w-7 text-graphite" />
            <p class="text-sm text-graphite">No staff members assigned.</p>
          </div>
          <div v-else>
            <div
              v-for="member in tenants.detail.staff"
              :key="member.id"
              class="flex items-center justify-between px-5 py-3 border-b border-slate-50 last:border-0"
            >
              <div>
                <p class="text-sm font-semibold text-ink">{{ member.username }}</p>
                <p class="text-xs text-graphite">{{ member.email }}</p>
              </div>
              <div class="flex items-center gap-3">
                <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-graphite capitalize">{{ member.role }}</span>
                <span class="text-xs text-graphite">Since {{ formatDate(member.joined_at) }}</span>
                <button
                  class="rounded-lg p-1.5 text-graphite hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  type="button"
                  title="Remove staff member"
                  :disabled="tenants.isSaving"
                  @click="tenants.removeStaff(tenants.detail!.id, member.id)"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent orders tab -->
      <div v-else-if="activeTab === 'orders'" class="space-y-3">
        <div class="rounded-xl border border-slate-200 bg-white shadow-panel overflow-hidden">
          <div class="border-b border-slate-100 px-5 py-3">
            <p class="text-sm font-semibold text-ink">Recent orders</p>
          </div>
          <div v-if="!tenants.detail.recent_orders.length" class="py-12 text-center text-sm text-graphite">
            No recent orders.
          </div>
          <div v-else>
            <div
              v-for="order in tenants.detail.recent_orders"
              :key="String(order.id)"
              class="flex items-center justify-between px-5 py-3 border-b border-slate-50 last:border-0"
            >
              <div>
                <p class="text-sm font-medium text-ink">{{ order.topic }}</p>
                <p class="text-xs text-graphite">#{{ order.id }}</p>
              </div>
              <div class="flex items-center gap-3">
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-medium capitalize"
                  :class="orderStatusClass(String(order.status))"
                >
                  {{ String(order.status).replace("_", " ") }}
                </span>
                <span class="text-sm font-semibold text-ink">${{ order.total_price }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Finance tab -->
      <div v-else-if="activeTab === 'finance'" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Total revenue</p>
            <p class="text-2xl font-bold text-ink">{{ tenants.money(tenants.detail.total_revenue) }}</p>
            <p class="text-xs text-graphite mt-1">All-time platform revenue from this tenant</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Avg order value</p>
            <p class="text-2xl font-bold text-ink">{{ tenants.money(tenants.detail.avg_order_value) }}</p>
            <p class="text-xs text-graphite mt-1">Average per completed order</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">30-day orders</p>
            <p class="text-2xl font-bold text-ink">{{ tenants.detail.recent_orders_30d ?? 0 }}</p>
            <p class="text-xs text-graphite mt-1">Orders placed in the last 30 days</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">New users (30d)</p>
            <p class="text-2xl font-bold text-ink">{{ tenants.detail.new_users_30d ?? 0 }}</p>
            <p class="text-xs text-graphite mt-1">New signups in the last 30 days</p>
          </div>
        </div>
        <div v-if="tenants.detail.metrics?.revenue" class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Revenue breakdown</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-graphite">Period revenue</p>
              <p class="text-base font-bold text-ink">{{ tenants.money(tenants.detail.metrics.revenue.total) }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">Avg per order</p>
              <p class="text-base font-bold text-ink">{{ tenants.money(tenants.detail.metrics.revenue.avg_per_order) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings tab -->
      <div v-else-if="activeTab === 'settings'" class="space-y-4">
        <!-- Feature flags -->
        <div class="rounded-xl border border-slate-200 bg-white shadow-panel overflow-hidden">
          <div class="border-b border-slate-100 px-5 py-3">
            <p class="text-sm font-semibold text-ink">Feature flags</p>
            <p class="text-xs text-graphite mt-0.5">Toggle which features are enabled for this tenant.</p>
          </div>
          <div>
            <div
              v-for="(enabled, flagKey) in tenants.detail.feature_flags"
              :key="flagKey"
              class="flex items-center justify-between px-5 py-3.5 border-b border-slate-50 last:border-0"
            >
              <div>
                <p class="text-sm font-medium text-ink">{{ flagLabel(flagKey) }}</p>
              </div>
              <button
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                :class="enabled ? 'bg-signal' : 'bg-slate-200'"
                type="button"
                :disabled="tenants.isSaving"
                @click="toggleFlag(flagKey)"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                  :class="enabled ? 'translate-x-6' : 'translate-x-1'"
                />
              </button>
            </div>
          </div>
        </div>

        <!-- Allowed subjects -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Allowed subjects</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="subject in tenants.detail.allowed_subjects"
              :key="subject"
              class="rounded-full border border-slate-200 px-3 py-1 text-xs text-graphite"
            >
              {{ subject }}
            </span>
          </div>
        </div>
      </div>

      <!-- Actions tab -->
      <div v-else-if="activeTab === 'actions'" class="space-y-4">
        <!-- Suspend -->
        <div
          v-if="tenants.detail.is_active !== false"
          class="rounded-xl border border-rose-200 bg-rose-50 p-5"
        >
          <p class="text-sm font-semibold text-rose-800 mb-1">Suspend tenant</p>
          <p class="text-xs text-rose-700 mb-3">
            Suspending stops all order placement and writer access for this site. Existing data is preserved.
          </p>
          <div v-if="!showSuspendConfirm">
            <button
              class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 transition-colors"
              type="button"
              @click="showSuspendConfirm = true"
            >
              Suspend tenant
            </button>
          </div>
          <div v-else class="space-y-3">
            <textarea
              v-model="suspendReason"
              rows="2"
              placeholder="Reason for suspension (optional)"
              class="w-full rounded-lg border border-rose-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
            />
            <div class="flex gap-2">
              <button
                class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-50 transition-colors"
                type="button"
                :disabled="tenants.isSaving"
                @click="handleSuspend"
              >
                {{ tenants.isSaving ? "Suspending…" : "Confirm suspension" }}
              </button>
              <button
                class="rounded-lg px-4 py-2 text-sm font-medium text-rose-700 hover:text-rose-800 transition-colors"
                type="button"
                @click="showSuspendConfirm = false; suspendReason = ''"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- Activate -->
        <div
          v-if="tenants.detail.is_active === false"
          class="rounded-xl border border-emerald-200 bg-emerald-50 p-5"
        >
          <p class="text-sm font-semibold text-emerald-800 mb-1">Reactivate tenant</p>
          <p class="text-xs text-emerald-700 mb-3">
            Restores full access for this tenant's writers, admins, and clients.
          </p>
          <button
            class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            type="button"
            :disabled="tenants.isSaving"
            @click="handleActivate"
          >
            {{ tenants.isSaving ? "Activating…" : "Reactivate tenant" }}
          </button>
        </div>

        <!-- Danger: edit config -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel">
          <p class="text-sm font-semibold text-ink mb-1">Edit configuration</p>
          <p class="text-xs text-graphite mb-3">Update billing email, support contact, or domain settings via the Settings tab.</p>
          <button
            class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50 transition-colors"
            type="button"
            @click="activeTab = 'settings'"
          >
            Go to Settings
          </button>
        </div>
      </div>
    </template>

    <div v-else-if="!tenants.isLoadingDetail && tenants.error" class="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center">
      <p class="text-sm font-semibold text-rose-800">{{ tenants.error }}</p>
      <button
        class="mt-3 text-sm text-rose-700 hover:text-rose-800 underline"
        type="button"
        @click="tenants.loadDetail(route.params.id as string)"
      >
        Retry
      </button>
    </div>
  </div>
</template>
