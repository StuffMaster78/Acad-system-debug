<script setup lang="ts">
const app = useAppUrl()
const config = useRuntimeConfig()

useHead({ title: 'Sign In | GradeCrest' })

// Forward any token query param to the portal's magic-link handler
onMounted(() => {
  const token = new URLSearchParams(window.location.search).get('token')
  const base  = config.public.appUrl || 'https://app.gradecrest.com'
  const target = token ? `${base}/auth/magic-link?token=${encodeURIComponent(token)}` : app.login
  window.location.replace(target)
})
</script>

<template>
  <div class="pt-16 min-h-screen flex items-center justify-center bg-mist">
    <div class="text-center space-y-3 px-4">
      <div class="flex size-12 items-center justify-center rounded-xl bg-gc-600 text-white text-lg font-extrabold mx-auto">G</div>
      <p class="text-sm text-graphite">Verifying your link…</p>
      <a :href="app.login" class="text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">Return to sign in</a>
    </div>
  </div>
</template>
