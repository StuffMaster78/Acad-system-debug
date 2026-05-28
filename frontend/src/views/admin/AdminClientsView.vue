<script setup lang="ts">
import { onMounted } from "vue";
import {
  Ban,
  CheckCircle2,
  KeyRound,
  RefreshCw,
  Search,
  ShieldAlert,
  UserRoundCheck,
  Users,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminClientsStore } from "@/stores/adminClients";

const clients = useAdminClientsStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filterOptions = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "suspended", label: "Suspended" },
  { key: "blacklisted", label: "Blacklisted" },
] as const;

function formatDate(value: string | null) {
  if (!value) return "Never";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(client: { isActive: boolean; isSuspended: boolean; isBlacklisted: boolean }) {
  if (client.isBlacklisted || client.isSuspended) return "danger";
  if (client.isActive) return "success";
  return "warning";
}

function statusLabel(client: { isActive: boolean; isSuspended: boolean; isBlacklisted: boolean }) {
  if (client.isBlacklisted) return "Blacklisted";
  if (client.isSuspended) return "Suspended";
  if (client.isActive) return "Active";
  return "Inactive";
}

onMounted(() => {
  clients.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Client management</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Client profiles enriched with account data, website context, spend,
          wallet state, loyalty, profile requests, and account actions.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="clients.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="clients.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ clients.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="clients.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ clients.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in clients.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(360px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <Users class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Clients across websites</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">
              Search by name, email, website, country, or loyalty tier.
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                v-for="option in filterOptions"
                :key="option.key"
                class="focus-ring min-h-9 rounded px-3 text-sm font-semibold"
                :class="clients.statusFilter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
                type="button"
                @click="clients.statusFilter = option.key"
              >
                {{ option.label }}
              </button>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="clients.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search clients"
              >
            </label>
          </div>
        </div>

        <div v-if="clients.filteredClients.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Client</th>
                <th class="px-3 py-2">Website</th>
                <th class="px-3 py-2">Wallet</th>
                <th class="px-3 py-2">Loyalty</th>
                <th class="px-3 py-2">Last login</th>
                <th class="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="client in clients.filteredClients"
                :key="client.id"
                class="cursor-pointer hover:bg-slate-50"
                :class="clients.selectedClient?.id === client.id ? 'bg-slate-50' : ''"
                @click="clients.selectedClient = client"
              >
                <td class="px-3 py-2.5">
                  <p class="font-semibold text-ink">{{ client.fullName }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ client.email }}</p>
                  <p class="mt-1 text-xs text-graphite">@{{ client.username }}</p>
                </td>
                <td class="px-3 py-2.5">
                  <p class="font-medium text-ink">{{ client.website }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ client.country }} · {{ client.timezone }}</p>
                </td>
                <td class="px-3 py-2.5">
                  <p class="font-semibold text-ink">{{ client.walletBalance }}</p>
                  <p class="mt-1 text-xs text-graphite">Spent {{ client.totalSpent }}</p>
                </td>
                <td class="px-3 py-2.5">
                  <p class="font-medium text-ink">{{ client.loyaltyTier }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ client.loyaltyPoints }} points</p>
                </td>
                <td class="px-3 py-2.5 text-graphite">
                  {{ formatDate(client.lastLogin) }}
                </td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="statusLabel(client)" :tone="statusTone(client)" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="Users"
            title="No clients found"
            message="Adjust the filter or refresh once the backend is connected."
          />
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <template v-if="clients.selectedClient">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold uppercase text-signal">Selected client</p>
                <h2 class="mt-2 text-xl font-semibold text-ink">
                  {{ clients.selectedClient.fullName }}
                </h2>
                <p class="mt-1 text-sm text-graphite">{{ clients.selectedClient.email }}</p>
              </div>
              <StatusPill
                :label="statusLabel(clients.selectedClient)"
                :tone="statusTone(clients.selectedClient)"
              />
            </div>

            <dl class="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div class="rounded-md border border-slate-200 p-3">
                <dt class="text-graphite">Website</dt>
                <dd class="mt-1 font-semibold text-ink">{{ clients.selectedClient.website }}</dd>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <dt class="text-graphite">Joined</dt>
                <dd class="mt-1 font-semibold text-ink">{{ formatDate(clients.selectedClient.dateJoined) }}</dd>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <dt class="text-graphite">Wallet</dt>
                <dd class="mt-1 font-semibold text-ink">{{ clients.selectedClient.walletBalance }}</dd>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <dt class="text-graphite">Spent</dt>
                <dd class="mt-1 font-semibold text-ink">{{ clients.selectedClient.totalSpent }}</dd>
              </div>
            </dl>

            <div class="mt-5">
              <p class="text-sm font-semibold text-ink">Preferred writers</p>
              <p class="mt-2 text-sm text-graphite">
                {{ clients.selectedClient.preferredWriters.length ? clients.selectedClient.preferredWriters.join(", ") : "None configured" }}
              </p>
            </div>

            <div class="mt-5 grid gap-2">
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
                type="button"
                :disabled="clients.isMutating"
                @click="clients.runClientAction('activate').catch(() => undefined)"
              >
                <UserRoundCheck class="h-4 w-4" />
                Activate
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 text-sm font-semibold text-amber-900"
                type="button"
                :disabled="clients.isMutating"
                @click="clients.runClientAction('suspend').catch(() => undefined)"
              >
                <ShieldAlert class="h-4 w-4" />
                Suspend
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
                type="button"
                :disabled="clients.isMutating"
                @click="clients.runClientAction('deactivate').catch(() => undefined)"
              >
                <Ban class="h-4 w-4" />
                Deactivate
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
                type="button"
                :disabled="clients.isMutating"
                @click="clients.resetPassword().catch(() => undefined)"
              >
                <KeyRound class="h-4 w-4" />
                Reset password
              </button>
            </div>
          </template>

          <EmptyState
            v-else
            :icon="Users"
            title="Select a client"
            message="Choose a row to review profile, wallet, loyalty, and account controls."
          />
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <CheckCircle2 class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Admin review queues</h2>
          </div>
          <div class="mt-4 space-y-3 text-sm">
            <div class="rounded-md border border-slate-200 p-3">
              <p class="font-semibold text-ink">Profile update requests</p>
              <p class="mt-1 text-graphite">{{ clients.profileRequests.length }} pending or recently submitted</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="font-semibold text-ink">Blacklisted emails</p>
              <p class="mt-1 text-graphite">{{ clients.blacklistedEmails.length }} entries visible to admins</p>
            </div>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>
