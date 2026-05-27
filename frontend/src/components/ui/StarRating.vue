<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    rating: number;
    max?: number;
    interactive?: boolean;
    size?: "sm" | "md" | "lg";
  }>(),
  { max: 5, interactive: false, size: "md" },
);

const emit = defineEmits<{ "update:rating": [value: number] }>();

const sizeClass = computed(() => ({
  sm: "h-3.5 w-3.5",
  md: "h-5 w-5",
  lg: "h-6 w-6",
}[props.size]));

function starFill(index: number): "full" | "partial" | "empty" {
  const val = props.rating - (index - 1);
  if (val >= 1) return "full";
  if (val > 0) return "partial";
  return "empty";
}

function select(value: number) {
  if (props.interactive) emit("update:rating", value);
}
</script>

<template>
  <div class="inline-flex items-center gap-0.5" :class="interactive ? 'cursor-pointer' : ''">
    <button
      v-for="i in max"
      :key="i"
      type="button"
      class="focus:outline-none"
      :class="interactive ? 'hover:scale-110 transition-transform' : 'pointer-events-none'"
      :aria-label="`${i} star${i > 1 ? 's' : ''}`"
      @click="select(i)"
    >
      <svg
        :class="[sizeClass, {
          'text-saffron': starFill(i) !== 'empty',
          'text-slate-200': starFill(i) === 'empty',
        }]"
        viewBox="0 0 24 24"
        fill="currentColor"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs v-if="starFill(i) === 'partial'">
          <linearGradient :id="`partial-${i}`" x1="0" x2="1" y1="0" y2="0">
            <stop :offset="`${((rating - Math.floor(rating)) * 100).toFixed(0)}%`" class="stop-saffron" stop-color="currentColor" />
            <stop :offset="`${((rating - Math.floor(rating)) * 100).toFixed(0)}%`" stop-color="#e2e8f0" />
          </linearGradient>
        </defs>
        <path
          :fill="starFill(i) === 'partial' ? `url(#partial-${i})` : 'currentColor'"
          d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
        />
      </svg>
    </button>
    <span v-if="rating > 0" class="ml-1 text-xs font-semibold text-graphite">
      {{ rating.toFixed(1) }}
    </span>
  </div>
</template>
