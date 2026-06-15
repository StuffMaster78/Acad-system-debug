<script setup lang="ts">
import { onMounted, reactive, watch } from "vue";
import { useCookieConsent } from "@/composables/useCookieConsent";

const consent = useCookieConsent();
const draft = reactive({
  preferences: false,
  analytics: false,
  marketing: false,
});

onMounted(async () => {
  await consent.init();
  Object.assign(draft, {
    preferences: consent.preferences.value.preferences,
    analytics: consent.preferences.value.analytics,
    marketing: consent.preferences.value.marketing,
  });
});

watch(consent.preferences, (value) => {
  Object.assign(draft, {
    preferences: value.preferences,
    analytics: value.analytics,
    marketing: value.marketing,
  });
});
</script>

<template>
  <div v-if="consent.bannerOpen.value" class="fixed inset-x-0 bottom-0 z-50 px-4 pb-4 sm:px-6">
    <div class="mx-auto max-w-5xl rounded-lg border border-slate-200 bg-white p-4 shadow-2xl">
      <div class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
        <div>
          <p class="text-sm font-bold text-ink">Cookie preferences</p>
          <p class="mt-1 max-w-3xl text-sm leading-6 text-graphite">
            We use necessary cookies for security, checkout, and remembering your choice. Optional cookies help us improve content, measure funnels, and personalize convenience features.
          </p>
          <button class="mt-2 text-sm font-semibold text-berry underline underline-offset-4" type="button" @click="consent.openSettings()">
            Manage settings
          </button>
        </div>
        <div class="flex flex-wrap gap-2 lg:justify-end">
          <button class="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50" type="button" @click="consent.rejectOptional()">
            Reject optional
          </button>
          <button class="rounded-md bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700" type="button" @click="consent.acceptAll()">
            Accept all
          </button>
        </div>
      </div>

      <div v-if="consent.settingsOpen.value" class="mt-4 border-t border-slate-200 pt-4">
        <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label class="rounded-md border border-slate-200 bg-slate-50 p-3">
            <span class="block text-sm font-semibold text-ink">Necessary</span>
            <span class="mt-1 block text-xs leading-5 text-graphite">Required for login, security, orders, and consent storage.</span>
            <input class="mt-3" type="checkbox" checked disabled>
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-ink">Preferences</span>
            <span class="mt-1 block text-xs leading-5 text-graphite">Saved UI state, bookmarks, reactions, and display choices.</span>
            <input v-model="draft.preferences" class="mt-3" type="checkbox">
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-ink">Analytics</span>
            <span class="mt-1 block text-xs leading-5 text-graphite">Aggregated page, funnel, and content performance measurement.</span>
            <input v-model="draft.analytics" class="mt-3" type="checkbox">
          </label>
          <label class="rounded-md border border-slate-200 p-3">
            <span class="block text-sm font-semibold text-ink">Marketing</span>
            <span class="mt-1 block text-xs leading-5 text-graphite">Campaign attribution and advertising integrations where enabled.</span>
            <input v-model="draft.marketing" class="mt-3" type="checkbox">
          </label>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button class="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50" type="button" @click="consent.rejectOptional()">
            Reject optional
          </button>
          <button class="rounded-md bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700" type="button" @click="consent.save(draft, 'settings')">
            Save settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
