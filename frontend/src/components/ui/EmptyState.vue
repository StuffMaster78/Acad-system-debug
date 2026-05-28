<script setup lang="ts">
import type { Component } from "vue";

defineProps<{
  icon: Component;
  title: string;
  message: string;
}>();
</script>

<template>
  <section class="flex flex-col items-center rounded-xl border border-dashed border-slate-300 bg-slate-50/60 px-6 py-12 text-center">
    <div class="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
      <component :is="icon" class="h-7 w-7 text-slate-400" aria-hidden="true" />
    </div>
    <h2 class="mt-4 text-base font-semibold text-ink">{{ title }}</h2>
    <p class="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-graphite">{{ message }}</p>
    <div v-if="$slots.action" class="mt-5">
      <slot name="action" />
    </div>
  </section>
</template>
