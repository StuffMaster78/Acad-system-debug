<template>
  <div class="engagement-stats flex flex-wrap items-center gap-6 text-sm text-gray-600">
    <!-- Views -->
    <div v-if="viewCount !== null" class="flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
      <span>{{ formatNumber(viewCount) }} {{ viewCount === 1 ? 'view' : 'views' }}</span>
    </div>

    <!-- Average Scroll Depth -->
    <div v-if="avgScrollPercent !== null && avgScrollPercent > 0" class="flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <span>Avg. scroll: {{ Math.round(avgScrollPercent) }}%</span>
    </div>

    <!-- CTA Clicks -->
    <div v-if="ctaClicks !== null && ctaClicks > 0" class="flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
      </svg>
      <span>{{ formatNumber(ctaClicks) }} {{ ctaClicks === 1 ? 'click' : 'clicks' }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  viewCount: {
    type: Number,
    default: null
  },
  avgScrollPercent: {
    type: Number,
    default: null
  },
  ctaClicks: {
    type: Number,
    default: null
  }
})

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>
.engagement-stats {
  /* Additional styling if needed */
}
</style>

