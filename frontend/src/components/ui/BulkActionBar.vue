<script setup lang="ts">
import { X } from "@lucide/vue";

export interface BulkAction {
  key: string;
  label: string;
  variant?: "default" | "danger" | "success";
  disabled?: boolean;
}

defineProps<{
  selectedCount: number;
  totalCount: number;
  actions: BulkAction[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  action: [key: string];
  clearSelection: [];
  selectAll: [];
}>();
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-200"
    enter-from-class="translate-y-4 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition-all duration-150"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-4 opacity-0"
  >
    <div
      v-if="selectedCount > 0"
      class="fixed bottom-6 left-1/2 z-50 -translate-x-1/2"
    >
      <div class="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-lg shadow-slate-900/10">
        <!-- Selection count + clear -->
        <div class="flex items-center gap-2 pr-3 border-r border-slate-200">
          <span class="text-sm font-semibold text-ink">{{ selectedCount }} selected</span>
          <button
            class="rounded-full p-0.5 text-slate-400 hover:text-ink"
            type="button"
            title="Clear selection"
            @click="emit('clearSelection')"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <!-- Select all -->
        <button
          v-if="selectedCount < totalCount"
          class="text-xs font-medium text-signal hover:underline"
          type="button"
          @click="emit('selectAll')"
        >
          Select all {{ totalCount }}
        </button>

        <!-- Action buttons -->
        <div class="flex items-center gap-2">
          <button
            v-for="action in actions"
            :key="action.key"
            type="button"
            class="rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors disabled:opacity-50"
            :class="{
              'bg-ink text-white hover:bg-ink/90': action.variant === 'default' || !action.variant,
              'bg-rose-600 text-white hover:bg-rose-700': action.variant === 'danger',
              'bg-emerald-600 text-white hover:bg-emerald-700': action.variant === 'success',
            }"
            :disabled="action.disabled || isLoading"
            @click="emit('action', action.key)"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>
