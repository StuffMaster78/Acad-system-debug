<script setup lang="ts">
const props = withDefaults(defineProps<{
  label: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}>(), {
  tone: "neutral",
});

const toneClasses: Record<string, string> = {
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger:  "border-rose-200 bg-rose-50 text-rose-800",
};

const dotClasses: Record<string, string> = {
  neutral: "bg-slate-400",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger:  "bg-rose-500",
};
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold leading-5"
    :class="toneClasses[props.tone]"
  >
    <span class="h-1.5 w-1.5 shrink-0 rounded-full" :class="dotClasses[props.tone]" aria-hidden="true" />
    {{ label }}
  </span>
</template>
