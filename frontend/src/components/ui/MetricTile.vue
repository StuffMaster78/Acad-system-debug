<script setup lang="ts">
import type { Component } from "vue";
import type { MetricDefinition } from "@/config/dashboard";

defineProps<{
  metric: MetricDefinition;
  icon?: Component;
}>();

const iconRing: Record<MetricDefinition["tone"], string> = {
  neutral: "bg-slate-100 text-slate-500",
  good: "bg-emerald-100 text-emerald-600",
  warn: "bg-amber-100 text-amber-600",
  risk: "bg-rose-100 text-rose-600",
};

const valueColor: Record<MetricDefinition["tone"], string> = {
  neutral: "text-ink",
  good: "text-emerald-700",
  warn: "text-amber-700",
  risk: "text-rose-700",
};
</script>

<template>
  <div class="flex rounded-lg border border-slate-200 bg-white p-4 transition-shadow hover:shadow-sm">
    <div class="flex flex-1 items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p class="text-[11px] font-semibold uppercase tracking-widest text-graphite">{{ metric.label }}</p>
        <p class="mt-1.5 text-2xl font-bold leading-none tabular-nums" :class="valueColor[metric.tone]">
          {{ metric.value }}
        </p>
        <p v-if="metric.detail" class="mt-1.5 text-xs leading-snug text-graphite">{{ metric.detail }}</p>
      </div>

      <div
        v-if="icon"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
        :class="iconRing[metric.tone]"
      >
        <component :is="icon" class="h-4 w-4" />
      </div>
    </div>
  </div>
</template>
