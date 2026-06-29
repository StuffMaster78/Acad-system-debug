<script setup lang="ts">
// Service pages are now canonical at /{slug}.
// This route issues a 301 so any /services/{slug} links or bookmarks
// land on the correct URL without breaking existing rankings.
const route = useRoute()
await navigateTo(`/${route.params.slug}`, { redirectCode: 301 })
</script>

<template><div /></template>
