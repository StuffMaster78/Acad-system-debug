<script setup lang="ts">
const consent = useCookieConsent()
const visible = ref(false)
const hovered = ref(false)

onMounted(async () => {
  await consent.init()
  // Show only after consent has been given (banner dismissed)
  watch(consent.bannerOpen, (open) => {
    if (!open) visible.value = true
  }, { immediate: true })
})
</script>

<template>
  <ClientOnly>
    <Transition
      enter-active-class="transition duration-500 ease-out delay-1000"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <button
        v-if="visible && !consent.bannerOpen.value"
        type="button"
        aria-label="Cookie settings"
        class="fixed bottom-24 right-5 z-40 flex items-center gap-2 overflow-hidden rounded-full border border-slate-200 bg-white shadow-md transition-all duration-200 hover:shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        :class="hovered ? 'pr-4' : 'pr-0'"
        @mouseenter="hovered = true"
        @mouseleave="hovered = false"
        @click="consent.openSettings(); consent.bannerOpen.value = true"
      >
        <!-- Cookie icon circle -->
        <span class="flex size-9 shrink-0 items-center justify-center rounded-full bg-amber-50 text-base">🍪</span>
        <!-- Expandable label -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 max-w-0"
          enter-to-class="opacity-100 max-w-[120px]"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100 max-w-[120px]"
          leave-to-class="opacity-0 max-w-0"
        >
          <span v-if="hovered" class="overflow-hidden whitespace-nowrap text-[11px] font-semibold text-slate-600">
            Cookie settings
          </span>
        </Transition>
      </button>
    </Transition>
  </ClientOnly>
</template>
