<script setup lang="ts">
const props = withDefaults(defineProps<{
  label: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}>(), {
  tone: "neutral",
});

const toneClasses = {
  neutral: "border-slate-200 bg-white text-graphite",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-rose-200 bg-rose-50 text-rose-800",
};
</script>

<template>
  <span
    class="inline-flex min-h-7 items-center rounded-md border px-2.5 text-xs font-semibold"
    :class="toneClasses[props.tone]"
  >
    {{ label }}
  </span>
</template>
