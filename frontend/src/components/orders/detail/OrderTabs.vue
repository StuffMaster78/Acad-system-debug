<template>
  <div class="flex gap-1 overflow-x-auto border-b border-slate-200">
    <button
      v-for="tab in visibleTabs"
      :key="tab"
      :disabled="isTabDimmed(tab)"
      @click="emit('update:modelValue', tab)"
      :class="[
        'whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors',
        modelValue === tab
          ? 'border-b-2 border-signal text-signal'
          : isTabDimmed(tab)
            ? 'text-slate-300 cursor-not-allowed'
            : 'text-graphite hover:text-ink',
      ]"
    >
      <span class="relative">
        {{ TAB_LABELS[tab] }}
        <span
          v-if="hasDot(tab)"
          class="absolute -right-2 -top-0.5 h-1.5 w-1.5 rounded-full bg-saffron"
        />
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { UserRole } from "@/types/roles";
import type { OrderLifecycle, OrderSummary } from "@/types/orders";
import { ROLE_TABS, TAB_LABELS } from "./types";

/** Tabs that remain usable even on terminal-state orders. */
const TERMINAL_TABS = new Set(["details", "timeline", "audit", "payments"]);

const props = defineProps<{
  role: UserRole;
  modelValue: string;
  order?: OrderSummary | null;
  lifecycle?: OrderLifecycle | null;
}>();

const emit = defineEmits<{ (e: "update:modelValue", tab: string): void }>();

const visibleTabs = computed(() => ROLE_TABS[props.role] ?? []);

const isTerminal = computed(() =>
  ["cancelled", "refunded", "archived"].includes(props.order?.status ?? "")
);

function isTabDimmed(tab: string): boolean {
  if (!isTerminal.value) return false;
  return !TERMINAL_TABS.has(tab);
}

const ADJUSTMENT_PENDING = new Set([
  "pending_client_response",
  "client_countered",
  "funding_pending",
]);

function hasDot(tab: string): boolean {
  if (tab !== "adjustments") return false;
  const s = props.lifecycle?.latest_adjustment_status;
  return !!s && ADJUSTMENT_PENDING.has(s);
}
</script>
