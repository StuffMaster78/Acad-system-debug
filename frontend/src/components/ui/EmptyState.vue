<script setup lang="ts">
import type { Component } from "vue";

defineProps<{
  icon: Component;
  title: string;
  message: string;
}>();
</script>

<template>
  <section class="rounded-md border border-dashed border-slate-300 bg-white p-8 text-center">
    <component :is="icon" class="mx-auto h-8 w-8 text-slate-400" aria-hidden="true" />
    <h2 class="mt-3 text-base font-semibold text-ink">{{ title }}</h2>
    <p class="mx-auto mt-2 max-w-md text-sm leading-6 text-graphite">{{ message }}</p>
  </section>
</template>
