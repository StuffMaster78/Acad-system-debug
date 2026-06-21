<script setup lang="ts">
import PromoStrip from '~/components/marketing/PromoStrip.vue'

const promo = usePromoDisplay()

onMounted(() => { void promo.init() })
</script>

<template>
  <NuxtLayout>
    <PromoStrip />
    <NuxtPage />
  </NuxtLayout>
</template>
