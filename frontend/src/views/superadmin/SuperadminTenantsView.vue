<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  Building2,
  CheckCircle2,
  ChevronRight,
  Globe,
  PauseCircle,
  Plus,
  Search,
  Users,
} from "@lucide/vue";
import { useTenantsStore } from "@/stores/tenants";
import type { TenantCreatePayload } from "@/types/superadmin";

const router = useRouter();
const tenants = useTenantsStore();

const suspendReason = ref("");
const showSuspendTarget = ref<number | null>(null);

onMounted(() => tenants.loadList());

function goToDetail(id: number) {
  router.push(`/superadmin/tenants/${id}`);
}

function statusClass(isActive?: boolean) {
  return isActive === false
    ? "bg-rose-50 text-rose-700 border-rose-200"
    : "bg-emerald-50 text-emerald-700 border-emerald-200";
}

function formatMoney(v: unknown) {
  return tenants.money(v);
}

async function submitCreate() {
  await tenants.createTenant();
}

function domainAutoSlug(form: TenantCreatePayload) {
  if (!form.slug && form.domain) {
    form.slug = form.domain.split(".")[0] ?? "";
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Tenants</h1>
        <p class="text-sm text-graphite mt-0.5">
          {{ tenants.activeTenants.length }} active · {{ tenants.inactiveTenants.length }} inactive
        </p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-ink/90 transition-colors"
        type="button"
        @click="tenants.openCreateModal()"
      >
        <Plus class="h-4 w-4" />
        New tenant
      </button>
    </div>

    <!-- Notice / Error -->
    <p v-if="tenants.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ tenants.notice }}</p>
    <p v-if="tenants.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ tenants.error }}</p>

    <!-- Filters -->
    <div class="flex items-center gap-3">
      <div class="relative flex-1 max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-graphite" />
        <input
          v-model="tenants.query"
          type="text"
          placeholder="Search tenants…"
          class="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
        />
      </div>
      <div class="flex items-center gap-1 rounded-lg border border-slate-200 p-1">
        <button
          v-for="opt in ([['all', 'All'], ['active', 'Active'], ['inactive', 'Inactive']] as const)"
          :key="opt[0]"
          class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
          :class="tenants.statusFilter === opt[0] ? 'bg-ink text-white' : 'text-graphite hover:text-ink'"
          type="button"
          @click="tenants.statusFilter = opt[0]"
        >
          {{ opt[1] }}
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="tenants.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-28 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="!tenants.filtered.length"
      class="flex flex-col items-center gap-2 rounded-xl border border-slate-200 py-16 text-center"
    >
      <Building2 class="h-8 w-8 text-graphite" />
      <p class="text-sm font-medium text-ink">No tenants found</p>
      <p class="text-xs text-graphite">Adjust your search or create a new tenant.</p>
    </div>

    <!-- Tenant cards -->
    <div v-else class="space-y-3">
      <div
        v-for="tenant in tenants.filtered"
        :key="tenant.id"
        class="group relative rounded-xl border border-slate-200 bg-white p-5 shadow-panel hover:border-slate-300 transition-colors cursor-pointer"
        @click="goToDetail(tenant.id)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-ink truncate">{{ tenant.name }}</span>
              <span
                class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
                :class="statusClass(tenant.is_active)"
              >
                <CheckCircle2 v-if="tenant.is_active !== false" class="h-3 w-3" />
                <PauseCircle v-else class="h-3 w-3" />
                {{ tenant.is_active !== false ? "Active" : "Inactive" }}
              </span>
            </div>
            <div class="mt-1 flex items-center gap-1.5 text-xs text-graphite">
              <Globe class="h-3 w-3" />
              <span>{{ tenant.domain }}</span>
              <span v-if="tenant.slug" class="text-slate-300">·</span>
              <span v-if="tenant.slug" class="font-mono">{{ tenant.slug }}</span>
            </div>
          </div>
          <ChevronRight class="h-4 w-4 text-slate-300 group-hover:text-graphite transition-colors mt-0.5 shrink-0" />
        </div>

        <!-- Stats row -->
        <div class="mt-4 grid grid-cols-4 gap-3">
          <div class="text-center">
            <p class="text-xs text-graphite">Revenue</p>
            <p class="text-sm font-bold text-ink">{{ formatMoney(tenant.total_revenue) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">Orders</p>
            <p class="text-sm font-bold text-ink">{{ (tenant.order_count ?? 0).toLocaleString() }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">Users</p>
            <p class="text-sm font-bold text-ink flex items-center justify-center gap-1">
              <Users class="h-3 w-3" />
              {{ (tenant.user_count ?? 0).toLocaleString() }}
            </p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">30d orders</p>
            <p class="text-sm font-bold text-ink">{{ tenant.recent_orders_30d ?? 0 }}</p>
          </div>
        </div>

        <!-- Completion rate bar if available -->
        <div
          v-if="tenant.metrics?.orders?.completion_rate != null"
          class="mt-3 flex items-center gap-2"
          @click.stop
        >
          <div class="h-1 flex-1 rounded-full bg-slate-100">
            <div
              class="h-1 rounded-full bg-emerald-500 transition-all"
              :style="{ width: `${tenant.metrics.orders.completion_rate}%` }"
            />
          </div>
          <span class="text-xs text-graphite shrink-0">{{ tenant.metrics.orders.completion_rate }}% completion</span>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="tenants.showCreateModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
        @click.self="tenants.showCreateModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
          <h2 class="text-base font-bold text-ink mb-4">New tenant</h2>
          <div class="space-y-3">
            <label class="block">
              <span class="text-xs font-semibold text-graphite uppercase tracking-wide">Name *</span>
              <input
                v-model="tenants.createForm.name"
                type="text"
                placeholder="WritePro Global"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold text-graphite uppercase tracking-wide">Domain *</span>
              <input
                v-model="tenants.createForm.domain"
                type="text"
                placeholder="site.example.com"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
                @blur="domainAutoSlug(tenants.createForm)"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold text-graphite uppercase tracking-wide">Slug *</span>
              <input
                v-model="tenants.createForm.slug"
                type="text"
                placeholder="site"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold text-graphite uppercase tracking-wide">Billing email</span>
              <input
                v-model="tenants.createForm.billing_email"
                type="email"
                placeholder="billing@site.com"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold text-graphite uppercase tracking-wide">Plan</span>
              <select
                v-model="tenants.createForm.plan_name"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              >
                <option value="Starter">Starter</option>
                <option value="Growth">Growth</option>
                <option value="Enterprise">Enterprise</option>
              </select>
            </label>
          </div>
          <div class="mt-5 flex justify-end gap-2">
            <button
              class="rounded-lg px-4 py-2 text-sm font-medium text-graphite hover:text-ink transition-colors"
              type="button"
              @click="tenants.showCreateModal = false"
            >
              Cancel
            </button>
            <button
              class="rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-ink/90 transition-colors disabled:opacity-50"
              type="button"
              :disabled="!tenants.createForm.name || !tenants.createForm.domain || !tenants.createForm.slug || tenants.isSaving"
              @click="submitCreate"
            >
              {{ tenants.isSaving ? "Creating…" : "Create tenant" }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
