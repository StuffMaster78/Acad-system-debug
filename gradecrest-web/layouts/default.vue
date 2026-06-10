<script setup lang="ts">
import SiteHeader from '~/components/layout/SiteHeader.vue'
import SiteFooter from '~/components/layout/SiteFooter.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-white font-sans text-ink antialiased">
    <SiteHeader />
    <main class="flex-1">
      <slot />
    </main>
    <SiteFooter />
  </div>
</template>
