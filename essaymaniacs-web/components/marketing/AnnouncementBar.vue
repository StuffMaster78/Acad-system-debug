<script setup lang="ts">
const dismissed = ref(false)

onMounted(() => {
  dismissed.value = sessionStorage.getItem('em-promo-bar') === '1'
})

function dismiss() {
  dismissed.value = true
  sessionStorage.setItem('em-promo-bar', '1')
}
</script>

<template>
  <div
    v-if="!dismissed"
    class="relative bg-brand-900 px-4 py-2.5 text-center text-sm text-white"
  >
    <span class="text-amber-300 font-semibold">First order?</span>
    <span> Use code </span>
    <code class="rounded bg-white/15 px-1.5 py-0.5 font-mono text-amber-200 font-bold">FIRST15</code>
    <span class="text-white/80"> for 15% off · Free plagiarism report included on every paper</span>
    <button
      class="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-white/50 transition-colors hover:text-white"
      aria-label="Dismiss announcement"
      @click="dismiss"
    >
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>
