<script setup lang="ts">
withDefaults(defineProps<{
  label: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}>(), { tone: "neutral" });

const cls: Record<string, string> = {
  neutral: "bg-slate-100 text-slate-600 ring-slate-200/60",
  success: "bg-emerald-100 text-emerald-800 ring-emerald-200/60",
  warning: "bg-amber-100 text-amber-800 ring-amber-200/60",
  danger:  "bg-rose-100 text-rose-700 ring-rose-200/60",
};
</script>

<template>
  <span
    class="inline-flex items-center whitespace-nowrap rounded-full px-2 py-0.5 text-[11px] font-semibold leading-4 ring-1"
    :class="cls[tone]"
  >
    {{ label }}
  </span>
</template>
