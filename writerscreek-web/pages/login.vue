<script setup lang="ts">
const appUrl = useAppUrl()

useSeoMeta({
  title: 'Writer Login | Writers Creek',
  description: 'Sign in to your Writers Creek writer account.',
})

onMounted(() => {
  window.location.href = appUrl.login
})
</script>

<template>
  <div class="flex min-h-[50vh] items-center justify-center bg-white px-4">
    <div class="text-center">
      <div class="mb-6 flex justify-center">
        <svg class="h-10 w-10 animate-spin text-brand-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
      </div>
      <p class="text-lg font-semibold text-slate-900">Redirecting to your writer dashboard…</p>
      <p class="mt-2 text-sm text-slate-500">
        Not redirected?
        <a :href="appUrl.login" class="font-medium text-brand-600 hover:underline">Click here</a>
      </p>
    </div>
  </div>
</template>
