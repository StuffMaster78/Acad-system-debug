<template>
  <section class="border-b border-slate-200 pb-5 space-y-4">
    <RouterLink
      :to="back"
      class="focus-ring inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold text-graphite hover:bg-slate-100"
    >
      <ArrowLeft class="h-4 w-4" />
      {{ backLabel }}
    </RouterLink>

    <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
      <div class="min-w-0">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Order #{{ orderId }}</p>
        <h1 class="mt-1 truncate text-2xl font-semibold text-ink">
          {{ order?.topic ?? "Loading…" }}
        </h1>

        <!-- Masked identities -->
        <div class="mt-2 flex flex-wrap items-center gap-3 text-sm text-graphite">
          <span class="font-mono">{{ clientDisplay }}</span>
          <span class="text-slate-300">·</span>
          <span class="font-mono">{{ writerDisplay }}</span>
          <span v-if="websiteLabel && isStaffRole" class="text-slate-300">·</span>
          <span v-if="websiteLabel && isStaffRole" class="text-xs">{{ websiteLabel }}</span>
        </div>
      </div>

      <!-- Status badges -->
      <div class="flex flex-wrap items-center gap-2 lg:shrink-0">
        <StatusPill :label="clientStatusLabel" />
        <StatusPill v-if="role !== 'writer' && order?.payment_status" :label="order.payment_status" tone="warning" />
        <span
          v-if="order?.is_urgent"
          class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
        >
          <Zap class="h-3 w-3" /> Urgent
        </span>
        <span v-if="riskLevel" :class="riskClass" class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold">
          <ShieldAlert class="h-3 w-3" />{{ riskLevel }}
        </span>
        <span v-if="visibleDeadline" class="ml-1 text-xs text-graphite">
          {{ deadlineCountdown(visibleDeadline) }}
        </span>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════
         CONTEXTUAL BANNERS — one per relevant state
    ══════════════════════════════════════════════════════════════ -->

    <!-- 1. Payment needed (client) -->
    <div
      v-if="showPaymentBanner"
      class="flex flex-col gap-3 rounded-lg border-2 border-sky-400 bg-sky-50 p-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <div class="flex items-start gap-3">
        <CreditCard class="mt-0.5 h-5 w-5 shrink-0 text-sky-600" />
        <div>
          <p class="text-sm font-semibold text-sky-900">Payment required to start your order</p>
          <p class="mt-0.5 text-xs text-sky-700">
            Your order has been placed but work cannot begin until payment is confirmed.
          </p>
        </div>
      </div>
      <button
        class="focus-ring inline-flex shrink-0 items-center gap-2 rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white"
        @click="emit('go-to-payments')"
      >
        <CreditCard class="h-4 w-4" /> Pay now
      </button>
    </div>

    <!-- 2. Finding a writer (client) -->
    <div
      v-if="showFindingWriterBanner"
      class="flex items-start gap-3 rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3"
    >
      <Clock class="mt-0.5 h-4 w-4 shrink-0 text-indigo-500" />
      <div>
        <p class="text-sm font-semibold text-indigo-900">We're finding a writer for your order</p>
        <p class="mt-0.5 text-xs text-indigo-700">
          Your order is in the queue. You'll be notified as soon as a writer is assigned.
        </p>
      </div>
    </div>

    <!-- 3. Order on hold -->
    <div
      v-if="showHoldBanner"
      class="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3"
    >
      <PauseCircle class="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-amber-900">This order is on hold</p>
        <p class="mt-0.5 text-xs text-amber-700">
          <template v-if="role === 'writer'">Work has been paused by the operations team. You'll be notified when it resumes.</template>
          <template v-else-if="isStaffRole">The order is currently paused. Use the ops panel to release the hold when ready.</template>
          <template v-else>Your order has been temporarily paused. Our team will resume it shortly.</template>
        </p>
      </div>
    </div>

    <!-- 4. Dispute under review -->
    <div
      v-if="showDisputeBanner"
      class="flex flex-col gap-3 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 sm:flex-row sm:items-start"
    >
      <ShieldAlert class="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-rose-900">Dispute open — under review by our team</p>
        <p class="mt-0.5 text-xs text-rose-700">
          <template v-if="role === 'client'">Your dispute has been received. Our support team is reviewing the case and will contact you.</template>
          <template v-else-if="role === 'writer'">A dispute has been raised on this order. Please do not make further changes until the team resolves it.</template>
          <template v-else>Active dispute — see Disputes section for details. Respond within SLA.</template>
        </p>
      </div>
    </div>

    <!-- 5. Terminal: cancelled -->
    <div
      v-if="order?.status === 'cancelled'"
      class="flex items-start gap-3 rounded-lg border border-slate-300 bg-slate-100 px-4 py-3"
    >
      <XCircle class="mt-0.5 h-4 w-4 shrink-0 text-slate-500" />
      <div>
        <p class="text-sm font-semibold text-slate-700">This order was cancelled</p>
        <p class="mt-0.5 text-xs text-slate-500">No further actions are available. Contact support if you believe this is an error.</p>
      </div>
    </div>

    <!-- 6. Terminal: refunded -->
    <div
      v-if="order?.status === 'refunded'"
      class="flex items-start gap-3 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3"
    >
      <CheckCircle2 class="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
      <div>
        <p class="text-sm font-semibold text-emerald-900">Refund issued</p>
        <p class="mt-0.5 text-xs text-emerald-700">
          <template v-if="role === 'client'">A refund has been processed. Please allow 3–5 business days for it to appear.</template>
          <template v-else>Refund has been processed. Check the Payments tab for details.</template>
        </p>
      </div>
    </div>

    <!-- 7. Terminal: archived -->
    <div
      v-if="order?.status === 'archived'"
      class="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
    >
      <Archive class="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
      <p class="text-xs text-slate-500">This order is archived. It is read-only and closed to further actions.</p>
    </div>

    <!-- 8. Approve delivery (client) -->
    <div
      v-if="showApproveBanner"
      class="flex flex-col gap-3 rounded-lg border-2 border-signal bg-emerald-50 p-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <div class="flex items-center gap-2">
        <ThumbsUp class="h-5 w-5 shrink-0 text-signal" />
        <p class="text-sm font-medium text-emerald-900">
          Delivery is ready. You have {{ lifecycle?.revision_window_days ?? 7 }} days to request a free revision after accepting.
        </p>
      </div>
      <button
        class="focus-ring inline-flex shrink-0 items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        type="button"
        :disabled="isMutating"
        @click="emit('approve')"
      >
        <Loader2 v-if="isMutating" class="h-4 w-4 animate-spin" />
        <ThumbsUp v-else class="h-4 w-4" />
        Accept delivery
      </button>
    </div>

    <!-- 9. Revision in progress (writer) -->
    <div
      v-if="showRevisionBanner"
      class="flex items-center gap-2 rounded-lg border border-saffron bg-amber-50 px-4 py-3"
    >
      <RotateCcw class="h-4 w-4 shrink-0 text-saffron" />
      <p class="text-sm text-amber-900">Revision requested — review the Revisions tab and re-submit your work.</p>
    </div>

    <!-- 10. Pending writer acceptance (writer) -->
    <div
      v-if="role === 'writer' && order?.status === 'pending_writer_acceptance'"
      class="flex items-start gap-3 rounded-lg border-2 border-signal bg-signal/5 px-4 py-3"
    >
      <ClipboardCheck class="mt-0.5 h-5 w-5 shrink-0 text-signal" />
      <div>
        <p class="text-sm font-semibold text-signal">You have a new direct assignment</p>
        <p class="mt-0.5 text-xs text-graphite">This order was assigned to you directly. Review the details below and accept or decline.</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import {
  Archive, ArrowLeft, CheckCircle2, ClipboardCheck, Clock, CreditCard,
  Loader2, PauseCircle, RotateCcw, ShieldAlert, ThumbsUp, XCircle, Zap,
} from "@lucide/vue";
import { useWebsitesStore } from "@/stores/websites";
import StatusPill from "@/components/ui/StatusPill.vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { maskedClient, maskedWriter, backRoute, deadlineCountdown, isStaff } from "./types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary | null;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
  isMutating?: boolean;
}>();

const emit = defineEmits<{
  (e: "approve"): void;
  (e: "go-to-payments"): void;
}>();

const back = computed(() => backRoute(props.role));
const backLabel = computed(() => {
  const map: Record<UserRole, string> = {
    client: "Orders", writer: "Assignments", support: "Orders",
    editor: "QA Queue", admin: "Orders", superadmin: "Orders",
  };
  return map[props.role] ?? "Back";
});

const isStaffRole = computed(() => isStaff(props.role));
const websites = useWebsitesStore();
const websiteLabel = computed(() => {
  if (!props.order?.website) return null;
  return websites.labelById(props.order.website) || `Site #${props.order.website}`;
});
const visibleDeadline = computed(() =>
  props.role === "writer" ? props.order?.writer_deadline : props.order?.client_deadline,
);

const clientDisplay = computed(() =>
  props.order ? maskedClient(props.order) : "—"
);
const writerDisplay = computed(() =>
  maskedWriter(props.lifecycle?.current_writer_id)
);

const riskLevel = computed(() => {
  const flags = props.order?.flags ?? [];
  if (flags.includes("high_risk")) return "High risk";
  if (flags.includes("at_risk")) return "At risk";
  return null;
});
const riskClass = computed(() => {
  if (riskLevel.value === "High risk") return "bg-red-100 text-red-700";
  if (riskLevel.value === "At risk") return "bg-amber-100 text-amber-700";
  return "";
});

// ── Status humanization for clients ──────────────────────────────────────────
const CLIENT_STATUS_LABELS: Record<string, string> = {
  created:                    "Pending payment",
  unpaid:                     "Pending payment",
  pending_payment:            "Payment processing",
  paid:                       "Finding a writer",
  ready_for_staffing:         "Finding a writer",
  pending_writer_acceptance:  "Assigning writer",
  in_progress:                "In progress",
  on_hold:                    "On hold",
  qa_review:                  "Under review",
  under_editing:              "Final editing",
  submitted:                  "Ready for your approval",
  completed:                  "Completed",
  revision_requested:         "Revision in progress",
  pending_cancellation:       "Cancellation under review",
  disputed:                   "Dispute open",
  cancelled:                  "Cancelled",
  refunded:                   "Refunded",
  archived:                   "Archived",
};

const clientStatusLabel = computed(() => {
  const raw = props.order?.status ?? "loading";
  if (props.role === "client") return CLIENT_STATUS_LABELS[raw] ?? raw.replace(/_/g, " ");
  return raw;
});

// ── Banner visibility ─────────────────────────────────────────────────────────

const showPaymentBanner = computed(() =>
  props.role === "client" &&
  ["created", "unpaid", "pending_payment"].includes(props.order?.status ?? "")
);

const showFindingWriterBanner = computed(() =>
  props.role === "client" &&
  ["paid", "ready_for_staffing"].includes(props.order?.status ?? "")
);

const showHoldBanner = computed(() =>
  props.order?.status === "on_hold" ||
  (!!props.lifecycle?.has_active_hold && props.order?.status === "in_progress")
);

const showDisputeBanner = computed(() =>
  props.order?.status === "disputed" ||
  !!props.lifecycle?.has_active_dispute
);

const showApproveBanner = computed(() => {
  if (props.role !== "client") return false;
  return props.lifecycle?.available_actions?.includes("approve_order") ?? false;
});

const showRevisionBanner = computed(() => {
  if (props.role !== "writer") return false;
  return (
    props.order?.status === "revision_requested" ||
    (props.lifecycle?.latest_revision_status != null &&
      !["resolved", "rejected", "withdrawn"].includes(props.lifecycle.latest_revision_status ?? ""))
  );
});
</script>
