<script setup lang="ts">
import type { OrderConfigOption } from "@/types/config";

defineProps<{
  label: string;
  options: OrderConfigOption[];
  placeholder?: string;
}>();

const model = defineModel<number | null>();
</script>

<template>
  <label class="block">
    <span class="text-sm font-medium text-graphite">{{ label }}</span>
    <select
      v-model.number="model"
      class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3"
    >
      <option :value="null">{{ placeholder || "Select an option" }}</option>
      <option v-for="option in options" :key="option.id" :value="option.id">
        {{ option.name }}
      </option>
    </select>
  </label>
</template>
