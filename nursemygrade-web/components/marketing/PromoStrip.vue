<script setup lang="ts">
import { X } from '@lucide/vue'

const { promo, visible, dismiss } = usePromoDisplay()

// Countdown — recomputed every second
const countdown = ref('')
let timer: ReturnType<typeof setInterval> | null = null

function tick() {
  if (!promo.value?.ends_at) { countdown.value = ''; return }
  const diff = new Date(promo.value.ends_at).getTime() - Date.now()
  if (diff <= 0) { countdown.value = ''; visible.value = false; return }
  const d = Math.floor(diff / 86400000)
  const h = Math.floor((diff % 86400000) / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  const s = Math.floor((diff % 60000) / 1000)
  countdown.value = d > 0
    ? `${d}d ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m`
    : `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
}

onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onUnmounted(() => { if (timer) clearInterval(timer) })

const isCountdown = computed(() => promo.value?.display_type === 'countdown_banner')
const isExternal  = (url?: string) => !!url && /^https?:\/\//.test(url)

const schemeClasses = computed(() => {
  const s = promo.value?.color_scheme || 'brand'
  if (s === 'dark') return 'bg-slate-900 text-white'
  if (s === 'warm') return 'bg-amber-500 text-white'
  return 'bg-brand-600 text-white'
})
const badgeClasses = computed(() => {
  const s = promo.value?.color_scheme || 'brand'
  if (s === 'dark') return 'bg-white/15 text-white'
  if (s === 'warm') return 'bg-white/20 text-white'
  return 'bg-white/20 text-white'
})
const ctaClasses = computed(() => {
  const s = promo.value?.color_scheme || 'brand'
  if (s === 'dark') return 'bg-white text-slate-900 hover:bg-slate-100'
  if (s === 'warm') return 'bg-white text-amber-700 hover:bg-amber-50'
  return 'bg-white text-brand-700 hover:bg-brand-50'
})
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="-translate-y-full opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="-translate-y-full opacity-0"
  >
    <div
      v-if="visible && promo?.active && promo.display_type !== 'popup'"
      :class="['relative z-40 w-full px-4 py-2.5 text-sm', schemeClasses]"
    >
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-3">

        <!-- Left: badge + headline -->
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <span
            v-if="promo.badge_text"
            :class="['shrink-0 rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider', badgeClasses]"
          >{{ promo.badge_text }}</span>
          <span class="font-semibold leading-snug">{{ promo.headline }}</span>
          <span v-if="promo.subtext" class="hidden opacity-80 sm:inline">{{ promo.subtext }}</span>
        </div>

        <!-- Centre: countdown (only for countdown_banner type) -->
        <div
          v-if="isCountdown && countdown"
          class="hidden shrink-0 font-mono text-base font-bold tabular-nums sm:block"
          aria-live="polite"
        >{{ countdown }}</div>

        <!-- Right: code + CTA + dismiss -->
        <div class="flex shrink-0 items-center gap-2">
          <code
            v-if="promo.discount_code"
            class="hidden rounded border border-white/30 bg-white/10 px-2 py-0.5 text-xs font-mono tracking-widest sm:inline"
          >{{ promo.discount_code }}</code>

          <a
            v-if="isExternal(promo.cta_url)"
            :href="promo.cta_url"
            :class="['rounded-lg px-3 py-1 text-xs font-bold transition-colors', ctaClasses]"
            @click="dismiss"
          >{{ promo.cta_label || 'Shop now' }}</a>
          <NuxtLink
            v-else
            :to="promo.cta_url || '/order'"
            :class="['rounded-lg px-3 py-1 text-xs font-bold transition-colors', ctaClasses]"
            @click="dismiss"
          >{{ promo.cta_label || 'Order now' }}</NuxtLink>

          <button
            class="ml-1 shrink-0 rounded p-1 opacity-70 transition-opacity hover:opacity-100"
            type="button"
            aria-label="Dismiss promotion"
            @click="dismiss"
          >
            <X class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>
