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
      {{ TAB_LABELS[tab] }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";
import { ROLE_TABS, TAB_LABELS } from "./types";

/** Tabs that remain usable even on terminal-state orders. */
const TERMINAL_TABS = new Set(["details", "timeline", "audit", "payments"]);

const props = defineProps<{
  role: UserRole;
  modelValue: string;
  order?: OrderSummary | null;
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
</script>
