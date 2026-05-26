<script setup lang="ts">
withDefaults(defineProps<{
  label?: string;
  size?: "sm" | "md" | "lg";
}>(), {
  label: "Loading",
  size: "md",
});

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-9 w-9",
};
</script>

<template>
  <div class="inline-flex items-center gap-2 text-sm font-medium text-graphite">
    <span
      class="inline-block animate-spin rounded-full border-2 border-slate-200 border-t-signal"
      :class="sizeClasses[size]"
      aria-hidden="true"
    />
    <span>{{ label }}</span>
  </div>
</template>
