<template>
  <div class="border-t border-slate-800 py-10">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold text-white">Nursing study tips in your inbox</p>
          <p class="mt-0.5 text-xs text-slate-400">Weekly care-plan guides, APA tips, and exclusive discounts. Unsubscribe any time.</p>
        </div>
        <form v-if="!success" class="flex w-full max-w-md gap-2" @submit.prevent="submit">
          <input
            v-model="email"
            type="email"
            required
            placeholder="your@email.com"
            class="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
          />
          <button
            type="submit"
            :disabled="busy"
            class="inline-flex shrink-0 items-center rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-800 disabled:opacity-60"
          >
            {{ busy ? '…' : 'Subscribe' }}
          </button>
        </form>
        <p v-else class="text-sm font-semibold text-emerald-400">
          ✓ You're subscribed! Check your inbox for a confirmation.
        </p>
      </div>
      <p v-if="errorMsg" class="mt-2 text-xs text-red-400">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const email   = ref('')
const busy    = ref(false)
const success = ref(false)
const errorMsg = ref('')

async function submit() {
  busy.value = true
  errorMsg.value = ''
  try {
    await $fetch(`${config.public.apiBase}/cms-api/newsletters/subscribe/`, {
      method: 'POST',
      body: { email: email.value, consent_marketing: true, source: 'footer', frequency: 'weekly' },
    })
    success.value = true
  } catch {
    errorMsg.value = 'Something went wrong — please try again.'
  } finally {
    busy.value = false
  }
}
</script>
