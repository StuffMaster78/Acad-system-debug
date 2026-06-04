<template>
  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <!-- Client: total, balance, deadline, revision window -->
    <template v-if="role === 'client'">
      <div v-for="card in clientCards" :key="card.label" class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">{{ card.label }}</p>
        <p class="mt-2 truncate font-semibold text-ink" :class="card.small ? 'text-base' : 'text-2xl'">{{ card.value }}</p>
        <p v-if="card.sub" class="mt-1 text-xs text-graphite">{{ card.sub }}</p>
      </div>
    </template>

    <!-- Writer: compensation, deadline, pages, status -->
    <template v-else-if="role === 'writer'">
      <div v-for="card in writerCards" :key="card.label" class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">{{ card.label }}</p>
        <p class="mt-2 truncate font-semibold text-ink" :class="card.small ? 'text-base' : 'text-2xl'">{{ card.value }}</p>
        <p v-if="card.sub" class="mt-1 text-xs text-graphite">{{ card.sub }}</p>
      </div>
    </template>

    <!-- Staff/admin: total, client deadline, writer deadline, writer payout -->
    <template v-else>
      <div v-for="card in adminCards" :key="card.label" class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">{{ card.label }}</p>
        <p class="mt-2 truncate font-semibold text-ink" :class="card.small ? 'text-base' : 'text-2xl'">{{ card.value }}</p>
        <p v-if="card.sub" class="mt-1 text-xs text-graphite">{{ card.sub }}</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { dateLabel, deadlineCountdown } from "./types";

const props = defineProps<{
  order: OrderSummary | null;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

function money(v: string | number | null | undefined, currency = "USD"): string {
  if (v === null || v === undefined || v === "") return `${currency} 0.00`;
  return `${currency} ${v}`;
}

interface Card { label: string; value: string; sub?: string; small?: boolean }

const clientCards = computed<Card[]>(() => [
  { label: "Total", value: money(props.order?.total_price, props.order?.currency), sub: `Paid ${money(props.order?.amount_paid, props.order?.currency)}` },
  { label: "Balance", value: money(props.order?.remaining_balance, props.order?.currency), sub: props.order?.payment_status ?? "—" },
  { label: "Client deadline", value: dateLabel(props.order?.client_deadline), sub: deadlineCountdown(props.order?.client_deadline), small: true },
  { label: "Revision window", value: props.lifecycle?.is_revision_window_open ? "Open" : "Closed", sub: `${props.lifecycle?.revision_window_days ?? 0} day window` },
]);

const writerCards = computed<Card[]>(() => [
  { label: "Compensation", value: money(props.order?.writer_compensation, props.order?.currency) },
  { label: "Your deadline", value: dateLabel(props.order?.writer_deadline), sub: deadlineCountdown(props.order?.writer_deadline), small: true },
  { label: "Pages / Qty", value: String(props.order?.base_quantity ?? props.order?.number_of_pages ?? "—"), sub: props.order?.spacing ?? "" },
  { label: "Status", value: props.order?.status ?? "—" },
]);

const adminCards = computed<Card[]>(() => [
  { label: "Total", value: money(props.order?.total_price, props.order?.currency), sub: props.order?.payment_status ?? "" },
  { label: "Client deadline", value: dateLabel(props.order?.client_deadline), sub: deadlineCountdown(props.order?.client_deadline), small: true },
  { label: "Writer deadline", value: dateLabel(props.order?.writer_deadline), sub: deadlineCountdown(props.order?.writer_deadline), small: true },
  { label: "Writer payout", value: money(props.order?.writer_compensation, props.order?.currency) },
]);
</script>
