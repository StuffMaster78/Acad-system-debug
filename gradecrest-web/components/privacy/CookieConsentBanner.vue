<script setup lang="ts">
const consent = useCookieConsent()

const draft = reactive({ preferences: false, analytics: false, marketing: false })

onMounted(async () => {
  await consent.init()
  Object.assign(draft, {
    preferences: consent.preferences.value.preferences,
    analytics:   consent.preferences.value.analytics,
    marketing:   consent.preferences.value.marketing,
  })
})

watch(consent.preferences, (v) => {
  Object.assign(draft, { preferences: v.preferences, analytics: v.analytics, marketing: v.marketing })
})

const CATEGORIES = [
  {
    key:   'preferences' as const,
    label: 'Preferences',
    icon:  '⚙️',
    desc:  'Saved UI state, bookmarks, and display choices.',
  },
  {
    key:   'analytics' as const,
    label: 'Analytics',
    icon:  '📊',
    desc:  'Page performance, funnel, and content measurement.',
  },
  {
    key:   'marketing' as const,
    label: 'Marketing',
    icon:  '📣',
    desc:  'Campaign attribution and advertising where enabled.',
  },
]
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="translate-y-4 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-4 opacity-0"
  >
    <div
      v-if="consent.bannerOpen.value"
      class="fixed inset-x-0 bottom-0 z-50 px-3 pb-3 sm:px-5 sm:pb-5"
      role="region"
      aria-label="Cookie consent"
    >
      <div class="mx-auto max-w-4xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl ring-1 ring-slate-950/5">

        <!-- ── Compact bar ──────────────────────────────────────────────── -->
        <div class="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-bold text-slate-900">We use cookies</p>
            <p class="mt-0.5 text-sm leading-relaxed text-slate-500">
              Necessary cookies keep the site secure. Optional cookies help us improve your experience and measure what's working.
              <NuxtLink to="/legal/privacy" class="font-medium text-brand-600 hover:underline">Privacy policy →</NuxtLink>
            </p>
          </div>
          <div class="flex shrink-0 flex-wrap gap-2">
            <button
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50"
              type="button"
              @click="consent.openSettings()"
            >Manage</button>
            <button
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50"
              type="button"
              @click="consent.rejectOptional()"
            >Reject optional</button>
            <button
              class="rounded-xl bg-brand-600 px-5 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand-700"
              type="button"
              @click="consent.acceptAll()"
            >Accept all</button>
          </div>
        </div>

        <!-- ── Settings panel ───────────────────────────────────────────── -->
        <div v-if="consent.settingsOpen.value" class="border-t border-slate-100 bg-slate-50/70 px-5 py-4">
          <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">

            <!-- Necessary — always on -->
            <div class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-green-100 text-base">🔒</div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-2">
                  <p class="text-xs font-bold text-slate-800">Necessary</p>
                  <span class="shrink-0 rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-bold text-green-700">Always on</span>
                </div>
                <p class="mt-0.5 text-[11px] leading-relaxed text-slate-500">Login, security, orders, and consent storage.</p>
              </div>
            </div>

            <!-- Optional categories -->
            <div
              v-for="cat in CATEGORIES"
              :key="cat.key"
              class="flex items-start gap-3 rounded-xl border bg-white p-3 transition-colors"
              :class="draft[cat.key] ? 'border-brand-200 ring-1 ring-brand-100' : 'border-slate-200'"
            >
              <div
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-base transition-colors"
                :class="draft[cat.key] ? 'bg-brand-100' : 'bg-slate-100'"
              >{{ cat.icon }}</div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-2">
                  <p class="text-xs font-bold text-slate-800">{{ cat.label }}</p>
                  <!-- Toggle switch -->
                  <button
                    role="switch"
                    :aria-checked="draft[cat.key]"
                    :aria-label="`${cat.label} cookies`"
                    class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-1"
                    :class="draft[cat.key] ? 'bg-brand-600' : 'bg-slate-200'"
                    type="button"
                    @click="draft[cat.key] = !draft[cat.key]"
                  >
                    <span
                      class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200"
                      :class="draft[cat.key] ? 'translate-x-[18px]' : 'translate-x-0.5'"
                    />
                  </button>
                </div>
                <p class="mt-0.5 text-[11px] leading-relaxed text-slate-500">{{ cat.desc }}</p>
              </div>
            </div>

          </div>

          <div class="mt-3 flex justify-end gap-2">
            <button
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-white"
              type="button"
              @click="consent.rejectOptional()"
            >Reject optional</button>
            <button
              class="rounded-xl bg-brand-600 px-5 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand-700"
              type="button"
              @click="consent.save(draft, 'settings')"
            >Save preferences</button>
          </div>
        </div>

      </div>
    </div>
  </Transition>
</template>
