<template>
  <section class="border-b border-slate-200 pb-5">
    <RouterLink
      :to="back"
      class="focus-ring inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm font-semibold text-graphite hover:bg-slate-100"
    >
      <ArrowLeft class="h-4 w-4" />
      {{ backLabel }}
    </RouterLink>

    <div class="mt-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
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
          <span v-if="order?.website && isStaffRole" class="text-slate-300">·</span>
          <span v-if="order?.website && isStaffRole" class="text-xs">
            Site #{{ order.website }}
          </span>
        </div>
      </div>

      <!-- Status badges + primary action -->
      <div class="flex flex-wrap items-center gap-2 lg:shrink-0">
        <StatusPill :label="order?.status ?? 'loading'" />
        <StatusPill v-if="order?.payment_status" :label="order.payment_status" tone="warning" />
        <span
          v-if="order?.is_urgent"
          class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
        >
          <Zap class="h-3 w-3" />
          Urgent
        </span>
        <span
          v-if="riskLevel"
          :class="riskClass"
          class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold"
        >
          <ShieldAlert class="h-3 w-3" />
          {{ riskLevel }}
        </span>
        <span v-if="order?.client_deadline" class="ml-1 text-xs text-graphite">
          {{ deadlineCountdown(order.client_deadline) }}
        </span>
      </div>
    </div>

    <!-- Approve delivery banner -->
    <div
      v-if="showApproveBanner"
      class="mt-4 flex flex-col gap-3 rounded-lg border-2 border-signal bg-emerald-50 p-4 sm:flex-row sm:items-center sm:justify-between"
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

    <!-- Revision in progress banner (writer) -->
    <div
      v-if="showRevisionBanner"
      class="mt-4 flex items-center gap-2 rounded-lg border border-saffron bg-amber-50 px-4 py-3"
    >
      <RotateCcw class="h-4 w-4 shrink-0 text-saffron" />
      <p class="text-sm text-amber-900">Revision requested — review the Revisions tab and re-submit your work.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { ArrowLeft, Loader2, RotateCcw, ShieldAlert, ThumbsUp, Zap } from "@lucide/vue";
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

const emit = defineEmits<{ (e: "approve"): void }>();

const back = computed(() => backRoute(props.role));
const backLabel = computed(() => {
  const map: Record<UserRole, string> = {
    client: "Orders", writer: "Assignments", support: "Orders",
    editor: "QA Queue", admin: "Orders", superadmin: "Orders",
  };
  return map[props.role] ?? "Back";
});

const isStaffRole = computed(() => isStaff(props.role));

const clientDisplay = computed(() => {
  if (props.role === "writer") return props.order ? maskedClient(props.order) : "—";
  return props.order ? maskedClient(props.order) : "—";
});

const writerDisplay = computed(() => maskedWriter(props.lifecycle?.current_writer_id));

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

const showApproveBanner = computed(() => {
  if (props.role !== "client") return false;
  const s = props.order?.status;
  return s === "delivered" || s === "awaiting_approval";
});

const showRevisionBanner = computed(() => {
  if (props.role !== "writer") return false;
  return props.order?.status === "revision_requested" ||
    (props.lifecycle?.latest_revision_status != null &&
      !["resolved", "rejected", "withdrawn"].includes(props.lifecycle.latest_revision_status ?? ""));
});
</script>
