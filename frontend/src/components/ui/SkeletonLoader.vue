<script setup lang="ts">
withDefaults(defineProps<{
  rows?: number;
  variant?: "lines" | "cards" | "table";
}>(), {
  rows: 3,
  variant: "lines",
});
</script>

<template>
  <div class="animate-pulse" aria-hidden="true">
    <div v-if="variant === 'table'" class="overflow-hidden rounded-md border border-slate-200 bg-white">
      <div class="grid grid-cols-4 gap-4 border-b border-slate-200 bg-slate-50 p-4">
        <span v-for="item in 4" :key="item" class="h-3 rounded bg-slate-200" />
      </div>
      <div v-for="row in rows" :key="row" class="grid grid-cols-4 gap-4 border-b border-slate-100 p-4 last:border-0">
        <span v-for="item in 4" :key="item" class="h-4 rounded bg-slate-100" />
      </div>
    </div>

    <div v-else-if="variant === 'cards'" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="row in rows" :key="row" class="h-28 rounded-md border border-slate-200 bg-white p-4">
        <div class="h-3 w-24 rounded bg-slate-200" />
        <div class="mt-5 h-7 w-20 rounded bg-slate-100" />
        <div class="mt-4 h-3 w-full rounded bg-slate-100" />
      </div>
    </div>

    <div v-else class="space-y-3">
      <div v-for="row in rows" :key="row" class="h-4 rounded bg-slate-100" />
    </div>
  </div>
</template>
