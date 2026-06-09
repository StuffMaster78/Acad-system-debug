<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const is404 = computed(() => props.error.statusCode === 404)
const is500 = computed(() => props.error.statusCode >= 500)

const title = computed(() => {
  if (is404.value) return 'Page not found'
  if (is500.value) return 'Something went wrong'
  return 'An error occurred'
})

const description = computed(() => {
  if (is404.value)
    return "The page you're looking for doesn't exist or has been moved. Check the URL or start from somewhere below."
  if (is500.value)
    return "We hit an unexpected error. Our team has been notified. Please try again in a moment."
  return props.error.statusMessage || "An unexpected error occurred. Please try again."
})

const suggestions = computed(() => {
  if (is404.value) return [
    { label: 'Home',     href: '/' },
    { label: 'Blog',     href: '/blog' },
    { label: 'Services', href: '/services' },
    { label: 'Pricing',  href: '/pricing' },
  ]
  return [
    { label: 'Home', href: '/' },
  ]
})

function handleError() {
  clearError({ redirect: '/' })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50">

    <!-- Minimal header -->
    <header class="border-b border-slate-200 bg-white px-6 py-4">
      <NuxtLink href="/" class="font-serif text-xl font-bold text-brand-700">
        NurseMyGrade
      </NuxtLink>
    </header>

    <main class="flex flex-1 items-center justify-center px-6 py-24">
      <div class="w-full max-w-md text-center">

        <!-- Status code -->
        <p class="text-8xl font-extrabold text-brand-100 select-none">
          {{ error.statusCode }}
        </p>

        <!-- Title -->
        <h1 class="mt-2 font-serif text-3xl font-bold text-slate-900">
          {{ title }}
        </h1>

        <!-- Description -->
        <p class="mt-4 text-base leading-7 text-slate-500">
          {{ description }}
        </p>

        <!-- Actions -->
        <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            class="inline-flex h-11 items-center rounded-lg bg-brand-700 px-6 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
            @click="handleError"
          >
            Go home
          </button>
          <button
            class="inline-flex h-11 items-center rounded-lg border border-slate-200 bg-white px-6 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
            @click="() => history.back()"
          >
            ← Go back
          </button>
        </div>

        <!-- Quick links for 404 -->
        <div v-if="is404" class="mt-10 border-t border-slate-200 pt-8">
          <p class="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Maybe one of these?
          </p>
          <div class="flex flex-wrap justify-center gap-2">
            <NuxtLink
              v-for="s in suggestions"
              :key="s.href"
              :href="s.href"
              class="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700"
            >
              {{ s.label }}
            </NuxtLink>
          </div>
        </div>

        <!-- Server error help -->
        <p v-if="is500" class="mt-8 text-xs text-slate-400">
          If this keeps happening, <NuxtLink href="/contact" class="underline hover:text-brand-700">contact support</NuxtLink>.
        </p>

      </div>
    </main>

  </div>
</template>
