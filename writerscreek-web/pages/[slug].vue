<script setup lang="ts">
const route = useRoute()
const slug = route.params.slug as string
</script>
<template>
  <BlogPostPage :slug="slug" />
</template>
