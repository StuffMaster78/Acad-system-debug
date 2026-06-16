<script setup lang="ts">
// Hiring-status announcement bar.
//
// Wagtail field mapping (TenantSEOSettings → Announcement Bar):
//   promo_bar_enabled → show / hide the bar
//   promo_code        → status key: "open" | "limited" | "closed"  (default: "closed")
//   promo_message     → the status sentence shown next to the badge
//   promo_suffix      → optional link label (e.g. "Join the waitlist →")
//
// No promo code or discount — this is a capacity/hiring gate, not a promotion.

const portal = usePortalStore()
const dismissed = ref(false)

const bar     = computed(() => portal.ctx.promo_bar)
const enabled = computed(() => bar.value?.enabled ?? true)
const status  = computed(() => (bar.value?.code || 'closed').toLowerCase())
const message = computed(() =>
  bar.value?.message ||
  (status.value === 'open'
    ? 'We are accepting new writers this month — limited spots available.'
    : status.value === 'limited'
    ? 'A small number of writer positions remain. Apply before this window closes.'
    : 'We have filled our writer slots for this hiring window. New applications open next month.')
)
const linkLabel = computed(() => bar.value?.suffix || '')

const badge = computed(() => {
  if (status.value === 'open')    return { label: 'NOW HIRING',          dot: 'bg-green-400',  text: 'text-green-400',  ring: 'ring-green-400/30',  bg: 'bg-green-400/10'  }
  if (status.value === 'limited') return { label: 'LIMITED SPOTS',       dot: 'bg-amber-400',  text: 'text-amber-400',  ring: 'ring-amber-400/30',  bg: 'bg-amber-400/10'  }
  return                                 { label: 'APPLICATIONS CLOSED', dot: 'bg-rose-400',   text: 'text-rose-400',   ring: 'ring-rose-400/30',   bg: 'bg-rose-400/10'   }
})

const ctaHref = computed(() =>
  status.value === 'open' || status.value === 'limited' ? '/apply' : '#'
)

onMounted(() => {
  dismissed.value = sessionStorage.getItem('wc-status-bar') === '1'
})

function dismiss() {
  dismissed.value = true
  sessionStorage.setItem('wc-status-bar', '1')
}
</script>

<template>
  <div
    v-if="enabled && !dismissed"
    class="relative bg-slate-950 px-10 py-2.5 text-center text-sm"
  >
    <!-- Status badge -->
    <span
      class="mr-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest ring-1"
      :class="[badge.text, badge.ring, badge.bg]"
    >
      <span class="h-1.5 w-1.5 rounded-full" :class="[badge.dot, status !== 'closed' ? 'animate-pulse' : '']" />
      {{ badge.label }}
    </span>

    <!-- Status message -->
    <span class="text-slate-300">{{ message }}</span>

    <!-- Optional CTA link -->
    <NuxtLink
      v-if="linkLabel && status !== 'closed'"
      :to="ctaHref"
      class="ml-3 font-semibold text-brand-400 transition-colors hover:text-brand-300"
    >{{ linkLabel }}</NuxtLink>

    <!-- Dismiss -->
    <button
      class="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-white/20 transition-colors hover:text-white/60"
      aria-label="Dismiss"
      @click="dismiss"
    >
      <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>
