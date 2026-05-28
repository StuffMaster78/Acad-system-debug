<template>
  <div class="space-y-4">
    <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <h2 class="text-base font-semibold text-ink">QA checklist</h2>
      <p class="mt-2 text-sm text-graphite">
        Quality checks, plagiarism report, AI detection, rubric compliance, and final approval live here.
      </p>
      <!-- TODO: wire order QA endpoint (/orders/{id}/qa/ or via orderOps) -->
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div v-for="item in checklist" :key="item.label" class="flex items-center justify-between rounded-md border border-slate-100 px-4 py-3">
          <span class="text-sm text-ink">{{ item.label }}</span>
          <span class="text-xs font-semibold" :class="item.done ? 'text-signal' : 'text-slate-400'">
            {{ item.done ? 'Passed' : 'Pending' }}
          </span>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-graphite">
      Plagiarism report, AI report, citation check, and final approval wiring requires the QA API endpoint. Backend service is in place.
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";

defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

// Placeholder checklist — TODO: replace with live QA data from /orders/{id}/qa/
const checklist = [
  { label: "Plagiarism check", done: false },
  { label: "AI detection", done: false },
  { label: "Rubric compliance", done: false },
  { label: "Formatting check", done: false },
  { label: "Citation check", done: false },
  { label: "Final approval", done: false },
];
</script>
