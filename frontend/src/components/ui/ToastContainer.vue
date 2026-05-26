<script setup lang="ts">
import { CheckCircle2, Info, TriangleAlert, XCircle } from "@lucide/vue";
import { useUiStore } from "@/stores/ui";

const ui = useUiStore();

const toastClasses = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  error: "border-rose-200 bg-rose-50 text-rose-900",
  warn: "border-amber-200 bg-amber-50 text-amber-900",
  info: "border-slate-200 bg-white text-ink",
};

const toastIcons = {
  success: CheckCircle2,
  error: XCircle,
  warn: TriangleAlert,
  info: Info,
};
</script>

<template>
  <div class="fixed right-4 top-4 z-[60] w-[min(380px,calc(100vw-2rem))] space-y-2">
    <article
      v-for="toast in ui.toasts"
      :key="toast.id"
      class="rounded-md border p-3 shadow-panel"
      :class="toastClasses[toast.type]"
      role="status"
    >
      <div class="flex items-start gap-3">
        <component :is="toastIcons[toast.type]" class="mt-0.5 h-4 w-4 shrink-0" />
        <p class="min-w-0 flex-1 text-sm font-medium leading-5">{{ toast.message }}</p>
        <button
          class="focus-ring rounded px-1 text-xs font-semibold"
          type="button"
          @click="ui.dismissToast(toast.id)"
        >
          Close
        </button>
      </div>
    </article>
  </div>
</template>
