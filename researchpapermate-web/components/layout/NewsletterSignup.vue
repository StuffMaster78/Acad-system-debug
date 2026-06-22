<script setup lang="ts">
const config   = useRuntimeConfig()
const email    = ref('')
const touched  = ref(false)
const busy     = ref(false)
const success  = ref(false)
const errorMsg = ref('')

const isValidEmail = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value))
const showInvalid  = computed(() => touched.value && email.value.length > 0 && !isValidEmail.value)

async function submit() {
  touched.value = true
  if (!isValidEmail.value) return
  busy.value = true; errorMsg.value = ''
  try {
    await $fetch(`${config.public.apiBase}/cms-api/newsletters/subscribe/`, {
      method: 'POST',
      body: { email: email.value, consent_marketing: true, source: 'blog_form', frequency: 'weekly' },
    })
    success.value = true
  } catch {
    errorMsg.value = 'Something went wrong — please try again.'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="border-t border-claret-800 py-14">
    <div class="mx-auto max-w-lg px-4 text-center">

      <!-- Icon -->
      <div class="mx-auto mb-4 flex size-11 items-center justify-center rounded-full bg-amber-500/20">
        <svg class="size-5 text-amber-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"/>
        </svg>
      </div>

      <h2 class="text-xl font-bold text-white sm:text-2xl">Research writing insights in your inbox</h2>
      <p class="mt-1.5 text-sm text-claret-300">APA, MLA, Chicago guides and methodology tips — delivered weekly.</p>

      <!-- Form -->
      <form v-if="!success" class="mt-6 space-y-3" @submit.prevent="submit" novalidate>
        <div class="flex flex-col gap-2 sm:flex-row">
          <input
            v-model="email"
            type="email"
            placeholder="Enter your email address"
            autocomplete="email"
            class="min-w-0 flex-1 rounded-xl border px-4 py-3 text-sm text-white placeholder:text-claret-600 focus:outline-none focus:ring-2 transition-colors"
            :class="showInvalid
              ? 'border-red-500/60 bg-red-950/20 focus:ring-red-500/20'
              : 'border-claret-700 bg-claret-900 focus:border-amber-500 focus:ring-amber-500/20'"
            @blur="touched = true"
            @input="touched = false"
          />
          <button
            type="submit"
            :disabled="busy"
            class="shrink-0 rounded-xl bg-amber-500 px-6 py-3 text-sm font-bold text-claret-950 transition-colors hover:bg-amber-400 disabled:opacity-60"
          >{{ busy ? 'Subscribing…' : 'Subscribe' }}</button>
        </div>

        <p v-if="showInvalid" class="text-left text-xs text-red-400">Please enter a valid email address!</p>
        <p v-else-if="errorMsg" class="text-left text-xs text-red-400">{{ errorMsg }}</p>

        <p class="text-xs text-claret-500">🔒 No spam · Unsubscribe any time</p>
        <p class="text-xs text-claret-600 leading-relaxed">
          By subscribing, I agree to receive email updates and promotional content, and I accept the
          <NuxtLink to="/privacy" class="underline underline-offset-2 hover:text-claret-400 transition-colors">Privacy Policy</NuxtLink>.
        </p>
      </form>

      <!-- Success -->
      <div v-else class="mt-6 flex flex-col items-center gap-3">
        <div class="flex size-12 items-center justify-center rounded-full bg-emerald-500/20">
          <svg class="size-6 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <p class="text-sm font-bold text-white">You're in! 🎉</p>
        <p class="text-xs text-claret-400">Check your inbox for a confirmation email.</p>
      </div>

    </div>
  </div>
</template>
