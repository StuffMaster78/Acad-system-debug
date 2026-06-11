<script setup lang="ts">
import { ArrowRight, Home, RefreshCw } from '@lucide/vue'

const props = defineProps<{ error: { statusCode: number; statusMessage?: string; message?: string } }>()
const route = useRoute()

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
  clearError({ redirect: route.fullPath })
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col">

    <!-- Top bar -->
    <div class="border-b border-slate-800 px-4 py-4 sm:px-6">
      <NuxtLink to="/" class="inline-flex items-center gap-2 text-sm font-bold text-white" @click.prevent="goHome">
        <span class="flex size-7 items-center justify-center rounded-lg bg-gc-600 text-white text-xs font-extrabold">G</span>
        GradeCrest
      </NuxtLink>
    </div>

    <!-- Main content -->
    <div class="flex flex-1 items-center justify-center px-4 py-20">
      <div class="w-full max-w-lg text-center space-y-6">

        <!-- Big status code -->
        <p class="text-[7rem] sm:text-[9rem] font-extrabold leading-none text-slate-800 select-none tabular-nums">
          {{ error.statusCode }}
        </p>

        <div class="-mt-4 space-y-3">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-400">
            {{ is404 ? 'Not Found' : is403 ? 'Forbidden' : is500 ? 'Server Error' : 'Error' }}
          </p>
          <h1 class="text-3xl font-bold text-white sm:text-4xl">{{ heading }}</h1>
          <p class="text-base text-slate-400 leading-relaxed max-w-sm mx-auto">{{ body }}</p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-7 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors"
            @click="goHome"
          >
            <Home class="size-4" />
            Back to homepage
          </button>
          <button
            v-if="is500"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-7 py-3.5 text-sm font-semibold text-slate-300 hover:border-slate-500 hover:text-white transition-colors"
            @click="reload"
          >
            <RefreshCw class="size-4" />
            Try again
          </button>
          <NuxtLink
            v-else
            to="/contact"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-7 py-3.5 text-sm font-semibold text-slate-300 hover:border-slate-500 hover:text-white transition-colors"
            @click="goHome"
          >
            Contact support
            <ArrowRight class="size-4" />
          </NuxtLink>
        </div>

        <!-- Quick links for 404 -->
        <div v-if="is404" class="pt-4 border-t border-slate-800">
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">You might be looking for</p>
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
              class="rounded-full border border-slate-700 px-4 py-1.5 text-sm text-slate-400 hover:border-gc-500 hover:text-gc-300 transition-colors"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer -->
    <div class="border-t border-slate-800 px-4 py-4 text-center text-xs text-slate-600">
      © {{ new Date().getFullYear() }} GradeCrest. All rights reserved.
    </div>

  </div>
</template>
