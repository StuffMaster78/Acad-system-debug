<script setup lang="ts">
const consent = useCookieConsent()
const draft = reactive({
  preferences: false,
  analytics: false,
  marketing: false,
})

onMounted(async () => {
  await consent.init()
  Object.assign(draft, {
    preferences: consent.preferences.value.preferences,
    analytics: consent.preferences.value.analytics,
    marketing: consent.preferences.value.marketing,
  })
})

watch(consent.preferences, (value) => {
  Object.assign(draft, {
    preferences: value.preferences,
    analytics: value.analytics,
    marketing: value.marketing,
  })
})

const show = computed(() => consent.bannerOpen.value)

function saveSettings() {
  return consent.save(draft, 'settings')
}
</script>

<template>
  <div v-if="show" class="fixed inset-x-0 bottom-0 z-50 px-4 pb-4 sm:px-6">
    <div class="mx-auto max-w-5xl rounded-lg border border-slate-200 bg-white p-4 shadow-2xl">
      <div class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
        <div>
          <p class="text-sm font-bold text-ink">Cookie preferences</p>
          <p class="mt-1 max-w-3xl text-sm leading-6 text-slate-600">
            We use necessary cookies for security, checkout, and remembering your choice. Optional cookies help us improve content, measure funnels, and personalize convenience features.
          </p>
          <button class="mt-2 text-sm font-semibold text-gc-700 underline underline-offset-4" type="button" @click="consent.openSettings()">
            Manage settings
          </button>
        </div>
        <div class="flex flex-wrap gap-2 lg:justify-end">
          <button class="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" type="button" @click="consent.rejectOptional()">
            Reject optional
          </button>
          <button class="rounded-md bg-gc-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gc-700" type="button" @click="consent.acceptAll()">
            Accept all
          </button>
        </div>
      </div>

      <div v-if="consent.settingsOpen.value" class="mt-4 border-t border-slate-200 pt-4">
        <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label class="rounded-md border border-slate-200 bg-slate-50 p-3">
            <span class="block text-sm font-semibold text-slate-900">Necessary</span>
            <span class="mt-1 block text-xs leading-5 text-slate-600">Required for login, security, orders, and consent storage.</span>
            <input class="mt-3" type="checkbox" checked disabled>
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-slate-900">Preferences</span>
            <span class="mt-1 block text-xs leading-5 text-slate-600">Saved form state, bookmarks, reactions, and display choices.</span>
            <input v-model="draft.preferences" class="mt-3" type="checkbox">
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-slate-900">Analytics</span>
            <span class="mt-1 block text-xs leading-5 text-slate-600">Aggregated page, funnel, and content performance measurement.</span>
            <input v-model="draft.analytics" class="mt-3" type="checkbox">
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-slate-900">Marketing</span>
            <span class="mt-1 block text-xs leading-5 text-slate-600">Campaign attribution and advertising integrations where enabled.</span>
            <input v-model="draft.marketing" class="mt-3" type="checkbox">
          </label>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button class="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" type="button" @click="consent.rejectOptional()">
            Reject optional
          </button>
          <button class="rounded-md bg-gc-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gc-700" type="button" @click="saveSettings()">
            Save settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
