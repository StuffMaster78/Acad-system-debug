<script setup lang="ts">
// 301 redirect: /services/:slug → /:slug (flat URL — SEO canonical is at the root level)
const slug = useRoute().params.slug as string
await navigateTo(`/${slug}`, { redirectCode: 301 })
</script>
<template><div /></template>
