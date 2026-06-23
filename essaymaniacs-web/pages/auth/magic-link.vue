<script setup lang="ts">
definePageMeta({ ssr: false })

const auth = useRpmAuthStore()
const app = useAppUrl()
const route = useRoute()

type State = 'loading' | 'success' | 'error'
const state = ref<State>('loading')

function buildAdoptUrl(access: string, refresh: string) {
  return `${app.dashboard}/auth/adopt#access=${encodeURIComponent(access)}&refresh=${encodeURIComponent(refresh)}`
}

onMounted(async () => {
  const token = route.query.token as string | undefined
  if (!token) {
    state.value = 'error'
    return
  }
  try {
    const tokens = await auth.confirmMagicLink(token)
    state.value = 'success'
    setTimeout(() => {
      window.location.href = buildAdoptUrl(tokens.access, tokens.refresh)
    }, 1000)
  } catch {
    state.value = 'error'
  }
})

  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
useSeoMeta({ robots: 'noindex' })
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-2xl border border-slate-200 bg-white p-10 shadow-lg shadow-slate-200/60 text-center">

        <template v-if="state === 'loading'">
          <svg class="mx-auto h-10 w-10 animate-spin text-brand-600" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
          </svg>
          <h1 class="mt-5 text-xl font-semibold text-slate-900">Signing you in…</h1>
          <p class="mt-2 text-sm text-slate-500">Verifying your magic link.</p>
        </template>

        <template v-else-if="state === 'success'">
          <svg class="mx-auto h-10 w-10 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <h1 class="mt-5 text-xl font-semibold text-slate-900">Signed in</h1>
          <p class="mt-2 text-sm text-slate-500">Redirecting to your dashboard…</p>
        </template>

        <template v-else>
          <svg class="mx-auto h-10 w-10 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <h1 class="mt-5 text-xl font-semibold text-slate-900">Link expired or invalid</h1>
          <p class="mt-2 text-sm text-slate-500">{{ auth.error || 'This link is invalid or has already been used.' }}</p>
          <NuxtLink
            to="/login"
            class="mt-5 inline-block text-sm font-semibold text-brand-600 hover:underline"
          >
            Back to sign in
          </NuxtLink>
        </template>

      </div>
    </section>
  </div>
</template>
