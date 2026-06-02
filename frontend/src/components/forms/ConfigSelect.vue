<script setup lang="ts">
import { computed } from "vue";
import type { OrderConfigOption } from "@/types/config";

const props = defineProps<{
  label: string;
  options: OrderConfigOption[];
  placeholder?: string;
  help?: string;
  required?: boolean;
}>();

const model = defineModel<number | null>();

const selected = computed(() => props.options.find((option) => option.id === model.value) ?? null);
const selectedHelp = computed(() => {
  const option = selected.value;
  if (!option) return props.help || "";
  return String(option.description || option.help_text || option.short_description || props.help || "");
});
</script>

<template>
  <label class="block">
    <span class="text-sm font-medium text-graphite">{{ label }}</span>
    <select
      v-model.number="model"
      class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
      :required="required"
    >
      <option :value="null">{{ placeholder || "Select an option" }}</option>
      <option v-for="option in options" :key="option.id" :value="option.id">
        {{ option.name }}
      </option>
    </select>
    <span v-if="selectedHelp" class="mt-1 block text-xs leading-5 text-graphite">
      {{ selectedHelp }}
    </span>
  </label>
</template>
