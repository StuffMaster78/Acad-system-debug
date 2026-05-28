<template>
  <div class="flex gap-1 overflow-x-auto border-b border-slate-200">
    <button
      v-for="tab in visibleTabs"
      :key="tab"
      @click="emit('update:modelValue', tab)"
      :class="[
        'whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors',
        modelValue === tab
          ? 'border-b-2 border-blue-600 text-blue-600'
          : 'text-graphite hover:text-ink',
      ]"
    >
      {{ TAB_LABELS[tab] }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { UserRole } from "@/types/roles";
import { ROLE_TABS, TAB_LABELS } from "./types";

const props = defineProps<{
  role: UserRole;
  modelValue: string;
}>();

const emit = defineEmits<{ (e: "update:modelValue", tab: string): void }>();

const visibleTabs = computed(() => ROLE_TABS[props.role] ?? []);
</script>
