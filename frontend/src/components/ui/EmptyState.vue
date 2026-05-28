<script setup lang="ts">
import type { Component } from "vue";

defineProps<{
  icon: Component;
  title: string;
  message: string;
}>();
</script>

<template>
  <section class="flex flex-col items-center py-12 text-center">
    <component :is="icon" class="h-8 w-8 text-slate-300" aria-hidden="true" />
    <p class="mt-3 text-sm font-semibold text-ink">{{ title }}</p>
    <p class="mx-auto mt-1 max-w-sm text-sm text-graphite">{{ message }}</p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action" />
    </div>
  </section>
</template>
