<script setup lang="ts">
import type { MetricDefinition } from "@/config/dashboard";

defineProps<{
  metric: MetricDefinition;
}>();

const toneClasses: Record<MetricDefinition["tone"], string> = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};
</script>

<template>
  <section
    class="min-h-32 rounded-md border p-4 shadow-panel"
    :class="toneClasses[metric.tone]"
  >
    <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
    <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
    <p class="mt-2 text-sm text-graphite">{{ metric.detail }}</p>
  </section>
</template>
