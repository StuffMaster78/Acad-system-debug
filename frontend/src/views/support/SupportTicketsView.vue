<script setup lang="ts">
import { onMounted } from "vue";
import {
  CheckCircle2,
  ExternalLink,
  LifeBuoy,
  Loader2,
  RefreshCw,
  Search,
  Siren,
} from "@lucide/vue";
import { RouterLink } from "vue-router";
import EmptyState from "@/components/ui/EmptyState.vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const support = useSupportWorkspaceStore();

const filterOptions = [
  { key: "all", label: "All" },
  { key: "mine", label: "Mine" },
  { key: "unassigned", label: "Unassigned" },
  { key: "high_priority", label: "High priority" },
  { key: "overdue", label: "Overdue" },
  { key: "escalated", label: "Escalated" },
] as const;

function statusTone(status?: string | null): "danger" | "warning" | "success" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s.includes("critical") || s.includes("escalated") || s.includes("breach")) return "danger";
  if (s.includes("open") || s.includes("progress") || s.includes("pending") || s.includes("high")) return "warning";
  if (s.includes("closed") || s.includes("resolved")) return "success";
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
  if (!support.tickets.length) support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Ticket queue</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          All support tickets — assigned, unassigned, escalated, and SLA-sensitive.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="support.isLoading"
        @click="support.hydrate().catch(() => undefined)"
      >
        <Loader2 v-if="support.isLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ support.error }}
    </p>
    <p v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ support.notice }}
    </p>

    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="inline-flex flex-wrap gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
        <button
          v-for="option in filterOptions"
          :key="option.key"
          class="focus-ring rounded-md px-3 py-2 text-xs font-semibold transition-colors"
          :class="support.filter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
          type="button"
          @click="support.filter = option.key"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="relative w-full lg:w-72">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          v-model="support.query"
          class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
          type="search"
          placeholder="Search tickets…"
        />
      </div>
    </div>

    <div class="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-panel">
      <div v-if="support.isLoading" class="space-y-px">
        <div
          v-for="n in 5"
          :key="n"
          class="animate-pulse border-b border-slate-100 px-5 py-4"
          aria-hidden="true"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 space-y-2">
              <div class="h-4 w-2/3 rounded bg-slate-200" />
              <div class="h-3 w-1/2 rounded bg-slate-100" />
            </div>
            <div class="h-6 w-20 rounded-full bg-slate-100" />
          </div>
        </div>
      </div>

      <div v-else-if="!support.filteredTickets.length" class="p-8">
        <EmptyState
          :icon="LifeBuoy"
          title="No tickets found"
          message="Adjust the filter or refresh to load tickets from the backend."
        />
      </div>

      <div v-else class="divide-y divide-slate-100">
        <article
          v-for="ticket in support.filteredTickets"
          :key="ticket.id"
          class="grid gap-4 px-5 py-4 hover:bg-slate-50 lg:grid-cols-[minmax(0,1fr)_auto]"
        >
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <p class="font-semibold text-ink">{{ ticket.title }}</p>
              <StatusPill :label="ticket.status" :tone="statusTone(ticket.status)" />
              <StatusPill :label="ticket.priority" :tone="statusTone(ticket.priority)" />
              <StatusPill v-if="ticket.is_escalated" label="escalated" tone="danger" />
              <StatusPill v-if="ticket.has_sla" label="SLA" tone="warning" />
            </div>
            <p class="mt-1.5 max-w-3xl text-sm leading-6 text-graphite">
              {{ ticket.description || "No description" }}
            </p>
            <p class="mt-1.5 text-xs text-graphite">
              {{ ticket.category || "general" }}
              · requester {{ ticket.created_by_name || "unknown" }}
              · assigned {{ ticket.assigned_to_name || ticket.assigned_to || "unassigned" }}
              · ref #{{ ticket.object_id || ticket.id }}
              · {{ formatDate(ticket.created_at) }}
            </p>
          </div>
          <div class="flex flex-wrap items-start gap-2 lg:justify-end">
            <RouterLink
              class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold text-ink hover:bg-slate-50"
              :to="`/support/tickets/${ticket.id}`"
            >
              <ExternalLink class="h-3.5 w-3.5" />
              View
            </RouterLink>
            <button
              class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
              type="button"
              :disabled="support.isMutating || ticket.status === 'closed'"
              @click="support.closeTicket(ticket.id).catch(() => undefined)"
            >
              <CheckCircle2 class="h-3.5 w-3.5" />
              Close
            </button>
            <button
              class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="support.isMutating || ticket.is_escalated"
              @click="support.escalateTicket(ticket.id).catch(() => undefined)"
            >
              <Siren class="h-3.5 w-3.5" />
              Escalate
            </button>
          </div>
        </article>
      </div>

      <Pagination
        v-if="!support.query && support.filter === 'all'"
        :page="1"
        :page-size="75"
        :count="support.tickets.length"
        @update:page="() => {}"
      />
    </div>
  </div>
</template>
