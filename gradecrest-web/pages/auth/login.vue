<script setup lang="ts">
const app = useAppUrl()

useHead({ title: 'Sign In | GradeCrest' }),
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
useSeoMeta({ robots: 'noindex, nofollow' })

onMounted(() => { window.location.replace(app.login) })
</script>

<template>
  <div class="pt-16 min-h-screen flex items-center justify-center bg-mist">
    <div class="text-center space-y-3 px-4">
      <div class="flex size-12 items-center justify-center rounded-xl bg-gc-600 text-white text-lg font-extrabold mx-auto">G</div>
      <p class="text-sm text-graphite">Redirecting to sign in…</p>
      <a :href="app.login" class="text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">Click here if not redirected</a>
    </div>
  </div>
</template>
