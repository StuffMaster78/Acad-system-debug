<script setup lang="ts">
/**
 * Custom chat launcher that wraps Tawk.to.
 * The Tawk.to widget is hidden (css: { visibility: 'hidden' }) so this
 * button is the only UI surface. Clicking it toggles the Tawk chat window.
 *
 * Set NUXT_PUBLIC_TAWKTO_PROPERTY_ID and NUXT_PUBLIC_TAWKTO_WIDGET_ID in
 * the site's .env to activate; leave blank to disable without errors.
 */
const config   = useRuntimeConfig()
const propId   = config.public.tawktoPropertyId as string | undefined
const widgetId = config.public.tawktoWidgetId   as string | undefined

const loaded    = ref(false)
const open      = ref(false)
const unread    = ref(0)

declare global {
  interface Window {
    Tawk_API?: {
      toggle?: () => void
      maximize?: () => void
      minimize?: () => void
      onLoad?: () => void
      onChatStarted?: () => void
      onChatMessageVisitor?: () => void
      onChatEnded?: () => void
      getUnreadMessagesCount?: () => number
    }
    Tawk_LoadStart?: Date
  }
}

onMounted(() => {
  if (!propId || !widgetId) return

  window.Tawk_API = window.Tawk_API ?? {}
  window.Tawk_LoadStart = new Date()

  const s = document.createElement('script')
  s.async = true
  s.src = `https://embed.tawk.to/${propId}/${widgetId}`
  s.charset = 'UTF-8'
  s.setAttribute('crossorigin', '*')
  document.head.appendChild(s)

  // Tawk callbacks
  window.Tawk_API.onLoad = () => {
    loaded.value = true
    // Hide the default Tawk button — we use our own
    ;(window.Tawk_API as any)?.hideWidget?.()
  }
  window.Tawk_API.onChatStarted  = () => { open.value = true }
  window.Tawk_API.onChatEnded    = () => { open.value = false }
})

function toggleChat() {
  if (!loaded.value) return
  window.Tawk_API?.toggle?.()
  open.value = !open.value
  unread.value = 0
}
</script>

<template>
  <ClientOnly>
    <!-- Only render when Tawk is configured -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-75"
      enter-to-class="opacity-100 scale-100"
    >
      <button
        v-if="propId && widgetId"
        type="button"
        aria-label="Live chat"
        class="fixed bottom-6 right-5 z-40 flex size-14 items-center justify-center rounded-full shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        :class="open ? 'bg-slate-800' : 'bg-brand-600'"
        @click="toggleChat"
      >
        <!-- Unread badge -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-50"
          enter-to-class="opacity-100 scale-100"
        >
          <span
            v-if="unread > 0 && !open"
            class="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white"
          >{{ unread }}</span>
        </Transition>

        <!-- Chat icon -->
        <svg
          v-if="!open"
          class="size-6 text-white"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
        </svg>

        <!-- Close icon when open -->
        <svg
          v-else
          class="size-5 text-white"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>

        <!-- Pulse ring when idle -->
        <span
          v-if="!open && loaded"
          class="absolute inset-0 rounded-full animate-ping bg-brand-400 opacity-20 pointer-events-none"
        />
      </button>
    </Transition>
  </ClientOnly>
</template>
