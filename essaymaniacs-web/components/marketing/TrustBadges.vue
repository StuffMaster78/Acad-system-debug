<script setup lang="ts">
// Set these to the live profile URLs once the accounts are created.
// Empty string = static badge (no link). Filled = clickable external link.
const TRUSTPILOT_URL = '' // e.g. 'https://www.trustpilot.com/review/essaymaniacs.com'
const SITEJABBER_URL = '' // e.g. 'https://www.sitejabber.com/reviews/essaymaniacs.com'
</script>

<template>
  <div class="flex flex-wrap items-center gap-3">

    <!-- Trustpilot -->
    <component
      :is="TRUSTPILOT_URL ? 'a' : 'div'"
      v-bind="TRUSTPILOT_URL ? { href: TRUSTPILOT_URL, target: '_blank', rel: 'noopener noreferrer' } : {}"
      class="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/20 transition-colors"
      :class="TRUSTPILOT_URL ? 'hover:bg-white/20 cursor-pointer' : ''"
    >
      <div class="flex gap-0.5">
        <svg v-for="i in 5" :key="i" class="h-3.5 w-3.5 text-[#00b67a]" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      </div>
      <span class="text-xs text-white">
        <strong>4.8</strong>
        <span class="ml-1 text-white/60">Trustpilot</span>
      </span>
    </component>

    <!-- Sitejabber -->
    <component
      :is="SITEJABBER_URL ? 'a' : 'div'"
      v-bind="SITEJABBER_URL ? { href: SITEJABBER_URL, target: '_blank', rel: 'noopener noreferrer' } : {}"
      class="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/20 transition-colors"
      :class="SITEJABBER_URL ? 'hover:bg-white/20 cursor-pointer' : ''"
    >
      <div class="flex gap-0.5">
        <svg v-for="i in 5" :key="i" class="h-3.5 w-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      </div>
      <span class="text-xs text-white">
        <strong>4.7</strong>
        <span class="ml-1 text-white/60">Sitejabber</span>
      </span>
    </component>

    <!-- Writers count -->
    <div class="flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/20">
      <span class="text-sm font-bold text-green-400">✓</span>
      <span class="text-xs text-white">
        <strong>500+</strong>
        <span class="ml-1 text-white/60">subject specialists</span>
      </span>
    </div>

    <!-- Papers delivered -->
    <div class="flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-2 ring-1 ring-white/20">
      <span class="text-sm font-bold text-green-400">✓</span>
      <span class="text-xs text-white">
        <strong>20,000+</strong>
        <span class="ml-1 text-white/60">essays delivered</span>
      </span>
    </div>

  </div>
</template>
