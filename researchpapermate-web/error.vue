<script setup lang="ts">
import { ArrowRight, Home, RefreshCw } from '@lucide/vue'

const props = defineProps<{ error: { statusCode: number; statusMessage?: string; message?: string } }>()

const is404 = computed(() => props.error.statusCode === 404)
const is403 = computed(() => props.error.statusCode === 403)
const is500 = computed(() => props.error.statusCode >= 500)

const heading = computed(() => {
  if (is404.value) return 'Page not found'
  if (is403.value) return 'Access denied'
  if (is500.value) return 'Something went wrong'
  return 'An error occurred'
})

const body = computed(() => {
  if (is404.value) return "The page you're looking for doesn't exist or may have been moved. Check the URL or head back to the homepage."
  if (is403.value) return "You don't have permission to access this page. If you think this is a mistake, please get in touch."
  if (is500.value) return "We hit an unexpected error on our end. Our team has been notified. Try refreshing, or come back in a few minutes."
  return "An unexpected error occurred. Please try again or return to the homepage."
})

function goHome() {
  clearError({ redirect: '/' })
}

function reload() {
  if (import.meta.client) {
    window.location.reload()
  } else {
    clearError({ redirect: '/' })
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-parchment-50">

    <!-- Top bar -->
    <div class="border-b border-parchment-200 bg-white px-4 py-4 sm:px-6">
      <NuxtLink to="/" class="inline-flex items-center gap-2" @click.prevent="goHome">
        <span class="font-serif text-xl font-extrabold text-claret-800">ResearchPaperMate</span>
      </NuxtLink>
    </div>

    <!-- Main content -->
    <div class="flex flex-1 items-center justify-center px-4 py-20">
      <div class="w-full max-w-lg space-y-6 text-center">

        <!-- Big status code -->
        <p class="select-none text-[7rem] font-extrabold leading-none text-claret-100 tabular-nums sm:text-[9rem]">
          {{ error.statusCode }}
        </p>

        <div class="-mt-4 space-y-3">
          <p class="text-xs font-semibold uppercase tracking-widest text-claret-400">
            {{ is404 ? 'Not Found' : is403 ? 'Forbidden' : is500 ? 'Server Error' : 'Error' }}
          </p>
          <h1 class="text-3xl font-bold text-claret-900 sm:text-4xl">{{ heading }}</h1>
          <p class="mx-auto max-w-sm text-base leading-relaxed text-slate-500">{{ body }}</p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col items-center justify-center gap-3 pt-2 sm:flex-row">
          <button
            class="inline-flex items-center gap-2 rounded-xl bg-claret-700 px-7 py-3.5 text-sm font-bold text-white transition-colors hover:bg-claret-800"
            @click="goHome"
          >
            <Home class="size-4" />
            Back to homepage
          </button>
          <button
            v-if="is500"
            class="inline-flex items-center gap-2 rounded-xl border border-parchment-300 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 transition-colors hover:border-claret-300 hover:text-claret-700"
            @click="reload"
          >
            <RefreshCw class="size-4" />
            Try again
          </button>
          <NuxtLink
            v-else
            to="/contact"
            class="inline-flex items-center gap-2 rounded-xl border border-parchment-300 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 transition-colors hover:border-claret-300 hover:text-claret-700"
            @click.prevent="clearError({ redirect: '/contact' })"
          >
            Contact support
            <ArrowRight class="size-4" />
          </NuxtLink>
        </div>

        <!-- Quick links for 404 -->
        <div v-if="is404" class="border-t border-parchment-200 pt-6">
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400">
            You might be looking for
          </p>
          <div class="flex flex-wrap justify-center gap-2">
            <NuxtLink
              v-for="link in [
                { label: 'Services', to: '/services' },
                { label: 'Pricing', to: '/pricing' },
                { label: 'How it works', to: '/how-it-works' },
                { label: 'Blog', to: '/blog' },
                { label: 'Contact', to: '/contact' },
              ]"
              :key="link.to"
              :to="link.to"
              class="rounded-full border border-parchment-300 bg-white px-4 py-1.5 text-sm text-slate-600 transition-colors hover:border-claret-300 hover:text-claret-700"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer -->
    <div class="border-t border-parchment-200 px-4 py-4 text-center text-xs text-slate-400">
      © {{ new Date().getFullYear() }} ResearchPaperMate. All rights reserved.
    </div>

  </div>
</template>
