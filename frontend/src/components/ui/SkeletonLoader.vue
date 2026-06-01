<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(defineProps<{
  rows?: number;
  variant?: "lines" | "cards" | "table" | "avatar-list" | "chips" | "detail";
}>(), {
  rows: 3,
  variant: "lines",
});

// Stagger line widths so it looks natural
const lineWidths = computed(() =>
  Array.from({ length: props.rows }, (_, i) =>
    ["100%", "85%", "70%", "90%", "60%"][i % 5],
  ),
);
</script>

<template>
  <div class="animate-pulse" aria-hidden="true" aria-label="Loading…">

    <!-- Table skeleton -->
    <div v-if="variant === 'table'" class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div class="grid grid-cols-5 gap-4 border-b border-slate-200 bg-slate-50 px-5 py-3">
        <span v-for="c in 5" :key="c" class="h-2.5 rounded-full bg-slate-200" />
      </div>
      <div v-for="row in rows" :key="row" class="grid grid-cols-5 gap-4 border-b border-slate-100 px-5 py-4 last:border-0">
        <span class="h-3.5 rounded-full bg-slate-200 col-span-2" />
        <span class="h-3.5 rounded-full bg-slate-100" />
        <span class="h-5 rounded-full bg-slate-200 w-16" />
        <span class="h-7 rounded-lg bg-slate-100 w-20" />
      </div>
    </div>

    <!-- Metric cards skeleton -->
    <div v-else-if="variant === 'cards'" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="row in rows" :key="row" class="h-32 rounded-xl border border-slate-200 bg-white p-5 space-y-3">
        <div class="h-2.5 w-24 rounded-full bg-slate-200" />
        <div class="h-8 w-16 rounded-lg bg-slate-100" />
        <div class="h-2.5 w-full rounded-full bg-slate-100" />
      </div>
    </div>

    <!-- Avatar list skeleton (writer/client cards) -->
    <div v-else-if="variant === 'avatar-list'" class="space-y-3">
      <div v-for="row in rows" :key="row" class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4">
        <div class="size-10 shrink-0 rounded-full bg-slate-200" />
        <div class="flex-1 space-y-2">
          <div class="h-3 w-1/3 rounded-full bg-slate-200" />
          <div class="h-2.5 w-2/3 rounded-full bg-slate-100" />
        </div>
        <div class="h-7 w-20 rounded-lg bg-slate-100" />
      </div>
    </div>

    <!-- Pill / chip row -->
    <div v-else-if="variant === 'chips'" class="flex flex-wrap gap-2">
      <div
        v-for="(w, i) in [72, 88, 64, 96, 80].slice(0, rows)"
        :key="i"
        class="h-7 rounded-full bg-slate-200"
        :style="{ width: w + 'px' }"
      />
    </div>

    <!-- Detail page skeleton (header + body) -->
    <div v-else-if="variant === 'detail'" class="space-y-6">
      <div class="rounded-xl border border-slate-200 bg-white p-6 space-y-4">
        <div class="h-4 w-1/4 rounded-full bg-slate-200" />
        <div class="h-7 w-2/3 rounded-lg bg-slate-200" />
        <div class="h-3 w-full rounded-full bg-slate-100" />
        <div class="h-3 w-5/6 rounded-full bg-slate-100" />
      </div>
      <div v-for="row in rows" :key="row" class="rounded-xl border border-slate-200 bg-white p-5 space-y-3">
        <div class="h-3 w-1/3 rounded-full bg-slate-200" />
        <div class="h-3 w-full rounded-full bg-slate-100" />
        <div class="h-3 w-4/5 rounded-full bg-slate-100" />
      </div>
    </div>

    <!-- Default: plain lines -->
    <div v-else class="space-y-2.5">
      <div
        v-for="(w, i) in lineWidths"
        :key="i"
        class="h-3.5 rounded-full bg-slate-200"
        :style="{ width: w }"
      />
    </div>

  </div>
</template>
