<script setup lang="ts">
const dismissed = ref(false)

onMounted(() => {
  dismissed.value = sessionStorage.getItem('gc-promo-bar') === '1'
})

function dismiss() {
  dismissed.value = true
  sessionStorage.setItem('gc-promo-bar', '1')
}
</script>

<template>
  <div
    v-if="!dismissed"
    class="relative bg-forest-950 px-10 py-2.5 text-center text-sm"
  >
    <!-- Gold left accent line -->
    <div class="pointer-events-none absolute inset-y-0 left-0 w-1 bg-gold-400" />

    <span class="font-semibold text-gold-400">First order?</span>
    <span class="text-white/70"> Use code </span>
    <code class="rounded bg-gold-400/20 px-1.5 py-0.5 font-mono text-xs font-bold text-gold-300 ring-1 ring-gold-400/30">GRADE15</code>
    <span class="text-white/70"> for 15% off</span>
    <span class="mx-2 text-white/30">·</span>
    <NuxtLink to="/order" class="font-semibold text-gc-400 transition-colors hover:text-gc-300">
      Start my paper →
    </NuxtLink>

    <button
      class="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-white/30 transition-colors hover:text-white"
      aria-label="Dismiss"
      @click="dismiss"
    >
      <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>
