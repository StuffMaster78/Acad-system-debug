<script setup lang="ts">
// iHuman Patients page is canonical at /ihuman-patients.
// This stub issues a 301 so old /services/ihuman-patients bookmarks and links land correctly.
await navigateTo('/ihuman-patients', { redirectCode: 301 })
</script>

<template><div /></template>
