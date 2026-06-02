<script setup lang="ts">
import { computed, onMounted } from "vue";
import {
  CheckCircle2,
  LifeBuoy,
  MessageSquareText,
  RefreshCw,
  Search,
  ShieldAlert,
  Siren,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import Pagination from "@/components/ui/Pagination.vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminSupportStore } from "@/stores/adminSupport";
import { useAuthStore } from "@/stores/auth";

const support = useAdminSupportStore();
const auth = useAuthStore();
const isSuperAdmin = computed(() => auth.role === "superadmin");

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filterOptions = [
  { key: "all", label: "All" },
  { key: "unassigned", label: "Unassigned" },
  { key: "high_priority", label: "High priority" },
  { key: "overdue", label: "Overdue" },
  { key: "escalated", label: "Escalated" },
] as const;

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("critical") || normalized.includes("escalated") || normalized.includes("breach")) {
    return "danger";
  }
  if (normalized.includes("open") || normalized.includes("progress") || normalized.includes("pending") || normalized.includes("high")) {
    return "warning";
  }
  if (normalized.includes("closed") || normalized.includes("resolved")) {
    return "success";
  }
  return "neutral";
}

onMounted(() => {
  support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Support operations</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Ticket queue, SLA pressure, escalations, and saved replies for the
          staff support desk.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="support.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="support.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ support.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="support.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ support.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in support.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(380px,0.8fr)]">
      <div class="rounded-xl border border-slate-200 bg-white">
        <!-- Header row -->
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <LifeBuoy class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold text-ink">Ticket queue</h2>
              <p class="text-xs text-graphite">Triage client, writer, billing, order, and technical support.</p>
            </div>
          </div>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-graphite">
            {{ support.filteredTickets.length }} ticket{{ support.filteredTickets.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <!-- Filters + search row -->
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
          <div class="flex flex-wrap gap-1">
            <button
              v-for="option in filterOptions"
              :key="option.key"
              class="focus-ring h-8 rounded-lg px-3 text-xs font-semibold transition-colors"
              :class="support.filter === option.key
                ? 'bg-ink text-white shadow-sm'
                : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
              type="button"
              @click="support.filter = option.key"
            >
              {{ option.label }}
            </button>
          </div>
          <label class="relative ml-auto block w-56">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="support.query"
              class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
              type="search"
              placeholder="Search tickets…"
            />
          </label>
        </div>

        <div v-if="support.filteredTickets.length" class="divide-y divide-slate-100">
          <article
            v-for="ticket in support.filteredTickets"
            :key="ticket.id"
            class="px-5 py-4"
          >
            <!-- Top row: title + pills + actions -->
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div class="flex min-w-0 flex-wrap items-center gap-2">
                <p class="font-semibold text-ink">{{ ticket.title }}</p>
                <StatusPill :label="ticket.status" :tone="statusTone(ticket.status)" />
                <StatusPill :label="ticket.priority" :tone="statusTone(ticket.priority)" />
                <StatusPill v-if="ticket.is_escalated" label="escalated" tone="danger" />
                <StatusPill v-if="ticket.has_sla" label="SLA" tone="warning" />
              </div>
              <div class="flex shrink-0 items-center gap-2">
                <button
                  class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
                  type="button"
                  :disabled="support.isMutating || ticket.status === 'closed'"
                  @click="support.closeTicket(ticket.id).catch(() => undefined)"
                >
                  <CheckCircle2 class="h-3.5 w-3.5 text-signal" />
                  Close
                </button>
                <!-- Escalate: hidden for superadmin — they ARE the escalation ceiling -->
                <button
                  v-if="!isSuperAdmin"
                  class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-3 text-xs font-semibold text-amber-700 hover:bg-amber-100 disabled:opacity-50"
                  type="button"
                  :disabled="support.isMutating || ticket.is_escalated"
                  @click="support.escalateTicket(ticket.id).catch(() => undefined)"
                >
                  <Siren class="h-3.5 w-3.5" />
                  Escalate
                </button>
              </div>
            </div>
            <!-- Description -->
            <p v-if="ticket.description" class="mt-2 text-sm leading-6 text-graphite line-clamp-2">
              {{ ticket.description }}
            </p>
            <!-- Meta row -->
            <div class="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span class="capitalize">{{ ticket.category || "general" }}</span>
              <span>·</span>
              <span>Client: <span class="text-graphite">{{ ticket.created_by_name || ticket.created_by || "—" }}</span></span>
              <span>·</span>
              <span>Assigned: <span class="text-graphite">{{ ticket.assigned_to_name || ticket.assigned_to || "unassigned" }}</span></span>
              <span>·</span>
              <span>{{ formatDate(ticket.created_at) }}</span>
            </div>
          </article>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="LifeBuoy"
            title="No tickets found"
            message="Adjust the queue filter or refresh after the backend is connected."
          />
        </div>

        <Pagination
          v-if="!support.query && support.filter === 'all'"
          :page="support.ticketPagination.page"
          :page-size="support.ticketPagination.pageSize"
          :count="support.ticketPagination.count"
          @update:page="support.fetchTickets($event).catch(() => undefined)"
        />
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <ShieldAlert class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Escalations</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Communication escalations needing staff resolution.</p>
          </div>

          <div v-if="support.escalations.length" class="divide-y divide-slate-100">
            <article
              v-for="escalation in support.escalations"
              :key="escalation.id"
              class="px-4 py-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">Thread #{{ escalation.thread }}</p>
                  <p class="mt-1 text-sm leading-5 text-graphite">{{ escalation.reason }}</p>
                </div>
                <StatusPill :label="escalation.status" :tone="statusTone(escalation.status)" />
              </div>
              <p class="mt-2 text-xs text-graphite">
                {{ escalation.escalated_by_display || "Staff" }} · {{ formatDate(escalation.escalated_at) }}
              </p>
              <button
                class="focus-ring mt-3 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                type="button"
                :disabled="support.isMutating || escalation.status === 'resolved'"
                @click="support.resolveEscalation(escalation.id).catch(() => undefined)"
              >
                <CheckCircle2 class="h-4 w-4" />
                Resolve
              </button>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="ShieldAlert"
              title="No escalations"
              message="Escalated communication threads will appear here."
            />
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <MessageSquareText class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Saved replies</h2>
            </div>
            <button
              class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
              type="button"
              :disabled="support.isMutating"
              @click="support.createSavedReply().catch(() => undefined)"
            >
              Save
            </button>
          </div>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input
                v-model="support.replyComposer.title"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Category</span>
              <input
                v-model="support.replyComposer.category"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Reply body</span>
              <RichTextEditor v-model="support.replyComposer.body" />
            </label>
          </div>

          <div class="mt-5 space-y-3">
            <article
              v-for="reply in support.savedReplies"
              :key="reply.id"
              class="rounded-md border border-slate-200 p-3"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ reply.title }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ reply.category || "general" }}</p>
                </div>
                <StatusPill :label="reply.is_active === false ? 'inactive' : 'active'" :tone="reply.is_active === false ? 'neutral' : 'success'" />
              </div>
              <div class="mt-2 text-sm leading-5 text-graphite" v-html="reply.body" />
            </article>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>
