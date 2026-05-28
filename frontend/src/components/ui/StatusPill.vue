<script setup lang="ts">
withDefaults(defineProps<{
  label: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}>(), { tone: "neutral" });

const cls: Record<string, string> = {
  neutral: "bg-slate-100 text-slate-600",
  success: "bg-emerald-100 text-emerald-800",
  warning: "bg-amber-100 text-amber-800",
  danger:  "bg-rose-100 text-rose-800",
};
</script>

<template>
  <span
    class="inline-flex items-center whitespace-nowrap rounded px-1.5 py-0.5 text-xs font-medium leading-4"
    :class="cls[tone]"
  >
    {{ label }}
  </span>
</template>
