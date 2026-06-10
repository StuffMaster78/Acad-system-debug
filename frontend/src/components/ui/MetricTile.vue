<script setup lang="ts">
import type { Component } from "vue";
import type { MetricDefinition } from "@/config/dashboard";

defineProps<{
  metric: MetricDefinition;
  icon?: Component;
}>();

</script>

<template>
  <div class="flex rounded-xl border border-slate-200 bg-white p-4 shadow-panel transition-shadow hover:shadow-card">
    <div class="flex flex-1 items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p class="text-[11px] font-medium uppercase tracking-widest text-graphite">
          {{ metric.label }}
        </p>
        <p class="mt-2 text-2xl font-semibold leading-none tabular-nums text-ink">
          {{ metric.value }}
        </p>
        <p v-if="metric.detail" class="mt-1.5 text-xs leading-snug text-graphite">
          {{ metric.detail }}
        </p>
      </div>

      <div
        v-if="icon"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100"
      >
        <component :is="icon" class="h-4 w-4 text-slate-500" />
      </div>
    </div>
  </div>
</template>
