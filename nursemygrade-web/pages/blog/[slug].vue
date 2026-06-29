<script setup lang="ts">
// Blog posts are canonical at /{slug}. This 301 ensures old /blog/{slug}
// bookmarks and inbound links land on the correct URL without losing rankings.
const route = useRoute()
await navigateTo(`/${route.params.slug}`, { redirectCode: 301 })
</script>

<template><div /></template>
