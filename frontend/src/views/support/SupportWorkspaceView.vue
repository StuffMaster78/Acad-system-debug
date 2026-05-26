<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  CheckCircle2,
  Clock3,
  CreditCard,
  FileWarning,
  LifeBuoy,
  MessageSquareText,
  RefreshCw,
  Search,
  ShieldAlert,
  Siren,
} from "@lucide/vue";
import RichTextEditor from "@/components/forms/RichTextEditor.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const route = useRoute();
const support = useSupportWorkspaceStore();

const filterOptions = [
  { key: "all", label: "All" },
  { key: "mine", label: "Mine" },
  { key: "unassigned", label: "Unassigned" },
  { key: "high_priority", label: "High priority" },
  { key: "overdue", label: "Overdue" },
  { key: "escalated", label: "Escalated" },
] as const;

const activeSection = computed(() => {
  if (route.path.includes("/tickets")) return "tickets";
  if (route.path.includes("/orders")) return "orders";
  if (route.path.includes("/escalations")) return "escalations";
  if (route.path.includes("/replies")) return "replies";
  return "queue";
});

const rescueBuckets = computed(() => [
  {
    label: "Disputed orders",
    value: support.orders.disputed_orders?.count ?? 0,
    detail: "Orders in dispute needing staff context.",
    icon: ShieldAlert,
  },
  {
    label: "Payment issues",
    value: support.orders.payment_issue_orders?.count ?? 0,
    detail: "Failed, pending, or mismatched payment states.",
    icon: CreditCard,
  },
  {
    label: "Pending refunds",
    value: support.orders.pending_refunds?.count ?? 0,
    detail: "Refund requests waiting for review.",
    icon: FileWarning,
  },
  {
    label: "Ticketed orders",
    value: support.orders.orders_with_tickets?.count ?? 0,
    detail: "Orders with linked support conversations.",
    icon: LifeBuoy,
  },
]);

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("critical") || normalized.includes("escalated") || normalized.includes("breach")) return "danger";
  if (normalized.includes("open") || normalized.includes("progress") || normalized.includes("pending") || normalized.includes("high") || normalized.includes("warning")) return "warning";
  if (normalized.includes("closed") || normalized.includes("resolved") || normalized.includes("track")) return "success";
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

function recordLabel(record: Record<string, unknown>): string {
  return String(record.topic ?? record.title ?? record.order_topic ?? `Record #${record.id ?? "unknown"}`);
}

onMounted(() => {
  support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support cockpit</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">
          Rescue queue
        </h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Tickets, order issues, SLA pressure, escalations, and saved replies for hands-on support operations.
        </p>
      </div>

      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="support.isLoading"
        @click="support.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="support.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ support.error }}
    </p>
    <p v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ support.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile v-for="metric in support.metrics" :key="metric.label" :metric="metric" />
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.75fr)]">
      <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <LifeBuoy class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold text-ink">
                {{ activeSection === "tickets" ? "Ticket queue" : "Active support desk" }}
              </h2>
            </div>
            <p class="mt-1 text-sm text-graphite">
              My assigned tickets, unassigned work, escalated cases, and SLA-sensitive issues.
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
                placeholder="Search tickets or order IDs"
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
                {{ ticket.category || "general" }} · requester {{ ticket.created_by_name || ticket.created_by || "unknown" }} · assigned {{ ticket.assigned_to_name || ticket.assigned_to || "unassigned" }} · ref #{{ ticket.object_id || ticket.id }} · {{ formatDate(ticket.created_at) }}
              </p>
            </div>
            <div class="flex flex-wrap items-start gap-2 lg:justify-end">
              <button
                class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                type="button"
                :disabled="support.isMutating || ticket.status === 'closed'"
                @click="support.closeTicket(ticket.id).catch(() => undefined)"
              >
                <CheckCircle2 class="h-4 w-4" />
                Close
              </button>
              <button
                class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700 disabled:opacity-60"
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
            title="No support tickets found"
            message="Adjust the filter or refresh once backend data is available."
          />
        </div>
      </div>

      <aside class="space-y-6">
        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-semibold text-ink">Rescue summary</h2>
              <p class="mt-1 text-sm text-graphite">Orders and disputes requiring attention.</p>
            </div>
            <StatusPill :label="`${support.rescueCount} active`" :tone="support.rescueCount ? 'warning' : 'success'" />
          </div>

          <div class="mt-4 grid gap-3">
            <div
              v-for="bucket in rescueBuckets"
              :key="bucket.label"
              class="rounded-md border border-slate-200 p-3"
            >
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <component :is="bucket.icon" class="h-4 w-4 text-signal" />
                  <p class="text-sm font-semibold text-ink">{{ bucket.label }}</p>
                </div>
                <span class="text-lg font-semibold text-ink">{{ bucket.value }}</span>
              </div>
              <p class="mt-1 text-xs text-graphite">{{ bucket.detail }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center gap-2">
            <Clock3 class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">SLA board</h2>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">On track</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ support.sla.active_status?.on_track ?? 0 }}</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Breached</p>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ support.sla.active_status?.breached ?? 0 }}</p>
            </div>
          </div>

          <div class="mt-4 space-y-2">
            <div
              v-for="deadline in support.sla.upcoming_deadlines ?? []"
              :key="String(deadline.id ?? deadline.order_id)"
              class="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-2 text-sm"
            >
              <span class="min-w-0 truncate text-graphite">Order #{{ deadline.order_id ?? deadline.order }}</span>
              <StatusPill :label="String(deadline.time_remaining_display ?? deadline.status ?? 'upcoming')" :tone="statusTone(String(deadline.status ?? 'warning'))" />
            </div>
          </div>
        </section>
      </aside>
    </section>

    <section class="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <ShieldAlert class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Escalations</h2>
        </div>
        <div class="mt-4 space-y-3">
          <article
            v-for="escalation in support.escalations"
            :key="escalation.id"
            class="rounded-md border border-slate-200 p-4"
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
              class="focus-ring mt-3 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
              type="button"
              :disabled="support.isMutating || escalation.status === 'resolved'"
              @click="support.resolveEscalation(escalation.id).catch(() => undefined)"
            >
              <CheckCircle2 class="h-4 w-4" />
              Resolve
            </button>
          </article>
          <EmptyState
            v-if="!support.escalations.length"
            :icon="ShieldAlert"
            title="No escalations"
            message="Escalated conversations will appear here."
          />
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <MessageSquareText class="h-5 w-5 text-signal" />
            <h2 class="text-lg font-semibold text-ink">Saved replies</h2>
          </div>
          <button
            class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
            type="button"
            :disabled="support.isMutating"
            @click="support.createSavedReply().catch(() => undefined)"
          >
            Save reply
          </button>
        </div>

        <div class="mt-4 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div class="space-y-3">
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

          <div class="space-y-3">
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
        </div>
      </div>
    </section>

    <section v-if="activeSection === 'orders' || activeSection === 'queue'" class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <div class="flex items-center gap-2">
        <FileWarning class="h-5 w-5 text-signal" />
        <h2 class="text-lg font-semibold text-ink">Order rescue details</h2>
      </div>
      <div class="mt-4 grid gap-4 lg:grid-cols-3">
        <div
          v-for="record in [
            ...(support.orders.disputed_orders?.orders ?? []),
            ...(support.orders.payment_issue_orders?.orders ?? []),
            ...(support.orders.pending_refunds?.refunds ?? []),
          ]"
          :key="String(record.id ?? record.order_id)"
          class="rounded-md border border-slate-200 p-4"
        >
          <p class="font-semibold text-ink">{{ recordLabel(record) }}</p>
          <p class="mt-1 text-sm text-graphite">
            Order #{{ record.order_id ?? record.id ?? "unknown" }} · {{ record.status ?? record.payment_status ?? "pending review" }}
          </p>
          <p v-if="record.reason" class="mt-2 text-sm text-graphite">{{ record.reason }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
