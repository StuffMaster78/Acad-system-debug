<script setup lang="ts">
import type { Component } from "vue";
import type { MetricDefinition } from "@/config/dashboard";

defineProps<{
  metric: MetricDefinition;
  icon?: Component;
}>();

const accent: Record<MetricDefinition["tone"], string> = {
  neutral: "bg-slate-400",
  good:    "bg-emerald-500",
  warn:    "bg-amber-400",
  risk:    "bg-rose-500",
};

const iconRing: Record<MetricDefinition["tone"], string> = {
  neutral: "bg-slate-100 text-slate-500",
  good:    "bg-emerald-100 text-emerald-600",
  warn:    "bg-amber-100 text-amber-600",
  risk:    "bg-rose-100 text-rose-600",
};

const valueColor: Record<MetricDefinition["tone"], string> = {
  neutral: "text-ink",
  good:    "text-emerald-700",
  warn:    "text-amber-700",
  risk:    "text-rose-700",
};
</script>

<template>
  <div class="relative flex overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md">
    <!-- Left accent bar -->
    <div class="w-1 shrink-0" :class="accent[metric.tone]" />

    <div class="flex flex-1 items-start justify-between gap-3 p-4">
      <div class="min-w-0">
        <p class="text-xs font-semibold uppercase tracking-wider text-graphite">{{ metric.label }}</p>
        <p class="mt-2 text-2xl font-bold leading-none" :class="valueColor[metric.tone]">
          {{ metric.value }}
        </p>
        <p class="mt-1.5 text-xs text-graphite leading-snug">{{ metric.detail }}</p>
      </div>

      <div
        v-if="icon"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
        :class="iconRing[metric.tone]"
      >
        <component :is="icon" class="h-4 w-4" />
      </div>
    </div>
  </div>
</template>
