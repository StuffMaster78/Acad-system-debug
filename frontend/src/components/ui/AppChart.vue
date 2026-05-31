<script setup lang="ts">
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import {
  LineChart,
  BarChart,
} from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import type { EChartsOption } from "echarts";

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

const props = withDefaults(
  defineProps<{
    option: EChartsOption;
    height?: string;
    loading?: boolean;
  }>(),
  { height: "320px", loading: false },
);
</script>

<template>
  <div :style="{ height, width: '100%' }" class="relative">
    <div
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center bg-white/70"
    >
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-berry border-t-transparent" />
    </div>
    <VChart
      :option="option"
      :style="{ height, width: '100%' }"
      autoresize
    />
  </div>
</template>
