<script setup lang="ts">
import { onMounted } from "vue";
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
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminSupportStore } from "@/stores/adminSupport";

const support = useAdminSupportStore();

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
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(380px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <LifeBuoy class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Ticket queue</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">
              Triage client, writer, billing, order, and technical support work.
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                v-for="option in filterOptions"
                :key="option.key"
                class="focus-ring min-h-9 rounded px-3 text-xs font-semibold"
                :class="support.filter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
                type="button"
                @click="support.filter = option.key"
              >
                {{ option.label }}
              </button>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="support.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search tickets"
              >
            </label>
          </div>
        </div>

        <div v-if="support.filteredTickets.length" class="divide-y divide-slate-100">
          <article
            v-for="ticket in support.filteredTickets"
            :key="ticket.id"
            class="grid gap-4 px-4 py-4 lg:grid-cols-[minmax(0,1fr)_auto]"
          >
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <p class="font-semibold text-ink">{{ ticket.title }}</p>
                <StatusPill :label="ticket.status" :tone="statusTone(ticket.status)" />
                <StatusPill :label="ticket.priority" :tone="statusTone(ticket.priority)" />
                <StatusPill v-if="ticket.is_escalated" label="escalated" tone="danger" />
                <StatusPill v-if="ticket.has_sla" label="SLA" tone="warning" />
              </div>
              <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
                {{ ticket.description || "No description" }}
              </p>
              <p class="mt-2 text-xs text-graphite">
                {{ ticket.category || "general" }} · client {{ ticket.created_by_name || ticket.created_by || "unknown" }} · assigned {{ ticket.assigned_to_name || ticket.assigned_to || "unassigned" }} · {{ formatDate(ticket.created_at) }}
              </p>
            </div>
            <div class="flex flex-wrap items-start gap-2 lg:justify-end">
              <button
                class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                type="button"
                :disabled="support.isMutating || ticket.status === 'closed'"
                @click="support.closeTicket(ticket.id).catch(() => undefined)"
              >
                <CheckCircle2 class="h-4 w-4" />
                Close
              </button>
              <button
                class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700"
                type="button"
                :disabled="support.isMutating"
                @click="support.escalateTicket(ticket.id).catch(() => undefined)"
              >
                <Siren class="h-4 w-4" />
                Escalate
              </button>
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
      </div>

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
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

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
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
