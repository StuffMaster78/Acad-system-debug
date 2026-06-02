<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  CheckCircle2,
  CreditCard,
  Gauge,
  Globe2,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  UserCog,
  XCircle,
} from "@lucide/vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSuperadminWorkspaceStore } from "@/stores/superadminWorkspace";

const route = useRoute();
const workspace = useSuperadminWorkspaceStore();

const roleOptions = ["admin", "support", "editor", "writer", "client"] as const;

const activeSection = computed(() => {
  if (route.path.includes("/tenants")) return "tenants";
  if (route.path.includes("/operations")) return "operations";
  if (route.path.includes("/finance")) return "finance";
  if (route.path.includes("/settings")) return "settings";
  return "command";
});

function statusTone(value: unknown) {
  const normalized = String(value ?? "").toLowerCase();
  if (normalized.includes("suspend") || normalized.includes("dispute") || normalized.includes("failed") || normalized.includes("inactive")) return "danger";
  if (normalized.includes("pending") || normalized.includes("probation") || normalized.includes("warning")) return "warning";
  if (normalized.includes("active") || normalized.includes("approved") || normalized.includes("completed")) return "success";
  return "neutral";
}

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

onMounted(() => {
  workspace.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Superadmin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Platform command</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Cross-tenant health, governance, revenue posture, appeals, and platform controls.
        </p>
      </div>

      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="workspace.isLoading"
        @click="workspace.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="workspace.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </p>
    <p v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile v-for="metric in workspace.metrics" :key="metric.label" :metric="metric" />
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
      <div class="rounded-lg border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <Globe2 class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold text-ink">
                {{ activeSection === "tenants" ? "Tenant registry" : "Tenant health" }}
              </h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Compare websites by users, orders, revenue, disputes, and support load.</p>
          </div>
          <StatusPill :label="`${workspace.activeTenants.length} active`" :tone="workspace.inactiveTenants.length ? 'warning' : 'success'" />
        </div>

        <div class="overflow-hidden">
          <div class="grid grid-cols-[1.2fr_auto_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Tenant</span>
            <span>Users</span>
            <span>Orders</span>
            <span class="text-right">Revenue</span>
          </div>
          <div
            v-for="tenant in workspace.tenants"
            :key="tenant.id"
            class="grid grid-cols-[1.2fr_auto_auto_auto] gap-3 border-t border-slate-100 px-4 py-4 text-sm"
          >
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="truncate font-semibold text-ink">{{ tenant.name || `Tenant #${tenant.id}` }}</p>
                <StatusPill :label="tenant.is_active === false ? 'inactive' : 'active'" :tone="tenant.is_active === false ? 'danger' : 'success'" />
              </div>
              <p class="mt-1 truncate text-xs text-graphite">{{ tenant.domain || tenant.slug || "No domain" }}</p>
            </div>
            <span class="font-semibold text-ink">{{ tenant.user_count ?? tenant.metrics?.users?.total ?? 0 }}</span>
            <span class="font-semibold text-ink">{{ tenant.recent_orders_30d ?? tenant.metrics?.orders?.total ?? tenant.order_count ?? 0 }}</span>
            <span class="text-right font-semibold text-ink">
              {{ workspace.money(tenant.total_revenue ?? tenant.metrics?.revenue?.total) }}
            </span>
          </div>
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Gauge class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">System health</h2>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Orders 24h</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.dashboard.system_health?.orders_last_24h ?? 0 }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">New users 7d</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.dashboard.system_health?.new_users_last_7d ?? 0 }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Overdue</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.dashboard.system_health?.overdue_orders ?? 0 }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Unassigned</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.dashboard.system_health?.unassigned_orders ?? 0 }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <CreditCard class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Finance posture</h2>
          </div>
          <div class="mt-4 space-y-3 text-sm">
            <div class="flex items-center justify-between">
              <span class="text-graphite">Pending payouts</span>
              <span class="font-semibold text-ink">{{ workspace.money(workspace.dashboard.pending_payouts) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-graphite">Completed payments</span>
              <span class="font-semibold text-ink">{{ workspace.money(workspace.dashboard.completed_payments) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-graphite">Refunded</span>
              <span class="font-semibold text-ink">{{ workspace.money(workspace.dashboard.total_refunds) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-graphite">Failed payments</span>
              <StatusPill :label="String(workspace.dashboard.failed_payments ?? 0)" :tone="workspace.dashboard.failed_payments ? 'danger' : 'success'" />
            </div>
          </div>
        </section>
      </aside>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <UserCog class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold text-ink">User governance</h2>
              <p class="text-xs text-graphite">Suspend, reactivate, and adjust platform roles.</p>
            </div>
          </div>
          <label class="relative block w-52">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="workspace.query"
              class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
              type="search"
              placeholder="Search users…"
            />
          </label>
        </div>

        <div class="divide-y divide-slate-100">
          <button
            v-for="user in workspace.filteredUsers"
            :key="user.id"
            class="grid w-full grid-cols-[1fr_auto] gap-3 px-4 py-3 text-left hover:bg-slate-50"
            :class="workspace.selectedUserId === user.id ? 'bg-slate-50' : 'bg-white'"
            type="button"
            @click="workspace.selectedUserId = user.id"
          >
            <span class="min-w-0">
              <span class="block truncate font-semibold text-ink">{{ user.username }}</span>
              <span class="mt-1 block truncate text-xs text-graphite">{{ user.email }} · {{ user.role }}</span>
            </span>
            <span class="flex flex-wrap justify-end gap-2">
              <StatusPill :label="user.is_suspended ? 'suspended' : 'active'" :tone="user.is_suspended ? 'danger' : 'success'" />
              <StatusPill v-if="user.is_on_probation" label="probation" tone="warning" />
            </span>
          </button>
        </div>

        <div class="border-t border-slate-200 p-4">
          <div class="grid gap-3 lg:grid-cols-[1fr_auto_auto_auto]">
            <input
              v-model="workspace.reason"
              class="focus-ring min-h-10 rounded-md border border-slate-200 px-3 text-sm"
              placeholder="Governance reason"
            >
            <select
              v-model="workspace.roleDraft"
              class="focus-ring min-h-10 rounded-md border border-slate-200 px-3 text-sm"
            >
              <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
            </select>
            <button
              class="focus-ring inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !workspace.selectedUserId"
              @click="workspace.changeSelectedUserRole().catch(() => undefined)"
            >
              Change role
            </button>
            <button
              class="focus-ring inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-rose-200 px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || !workspace.selectedUserId"
              @click="workspace.suspendSelectedUser().catch(() => undefined)"
            >
              Suspend
            </button>
            <button
              class="focus-ring inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-emerald-200 px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60 lg:col-start-4"
              type="button"
              :disabled="workspace.isMutating || !workspace.selectedUserId"
              @click="workspace.reactivateSelectedUser().catch(() => undefined)"
            >
              Reactivate
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <ShieldAlert class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Appeals</h2>
          </div>
          <div class="mt-4 space-y-3">
            <article
              v-for="appeal in workspace.appeals"
              :key="appeal.id"
              class="rounded-md border border-slate-200 p-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ appeal.user_username || appeal.user_email || `Appeal #${appeal.id}` }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ appeal.reason || "No appeal reason supplied." }}</p>
                  <p class="mt-2 text-xs text-graphite">{{ appeal.appeal_type || "appeal" }} · {{ formatDate(appeal.submitted_at) }}</p>
                </div>
                <StatusPill :label="appeal.status || 'pending'" :tone="statusTone(appeal.status || 'pending')" />
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <button
                  class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-emerald-200 px-3 text-xs font-semibold text-emerald-800 disabled:opacity-60"
                  type="button"
                  :disabled="workspace.isMutating || appeal.status !== 'pending'"
                  @click="workspace.reviewAppeal(appeal.id, 'approve').catch(() => undefined)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Approve
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-rose-200 px-3 text-xs font-semibold text-rose-700 disabled:opacity-60"
                  type="button"
                  :disabled="workspace.isMutating || appeal.status !== 'pending'"
                  @click="workspace.reviewAppeal(appeal.id, 'reject').catch(() => undefined)"
                >
                  <XCircle class="h-4 w-4" />
                  Reject
                </button>
              </div>
            </article>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <ShieldCheck class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Governance log</h2>
          </div>
          <div class="mt-4 space-y-3">
            <article
              v-for="log in workspace.logs"
              :key="log.id"
              class="rounded-md border border-slate-200 p-3"
            >
              <p class="text-sm font-semibold text-ink">{{ log.action_type || "Action" }}</p>
              <p class="mt-1 text-sm text-graphite">{{ log.action_details || "No details." }}</p>
              <p class="mt-2 text-xs text-slate-500">{{ log.formatted_timestamp || formatDate(log.timestamp) }}</p>
            </article>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>
