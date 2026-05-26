<script setup lang="ts">
import { computed } from "vue";
import { ChevronLeft, ChevronRight } from "@lucide/vue";

const props = defineProps<{
  page: number;
  pageSize: number;
  count: number;
}>();

const emit = defineEmits<{ "update:page": [page: number] }>();

const pageCount = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)));
const from = computed(() => Math.min((props.page - 1) * props.pageSize + 1, props.count));
const to = computed(() => Math.min(props.page * props.pageSize, props.count));
</script>

<template>
  <div
    v-if="count > pageSize"
    class="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-3 text-sm"
  >
    <p class="text-graphite">
      {{ from }}–{{ to }} of {{ count }}
    </p>
    <div class="flex items-center gap-1">
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 text-ink disabled:opacity-40"
        type="button"
        :disabled="page <= 1"
        aria-label="Previous page"
        @click="emit('update:page', page - 1)"
      >
        <ChevronLeft class="h-4 w-4" />
      </button>
      <span class="min-w-[4rem] text-center font-medium text-ink">
        {{ page }} / {{ pageCount }}
      </span>
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 text-ink disabled:opacity-40"
        type="button"
        :disabled="page >= pageCount"
        aria-label="Next page"
        @click="emit('update:page', page + 1)"
      >
        <ChevronRight class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
