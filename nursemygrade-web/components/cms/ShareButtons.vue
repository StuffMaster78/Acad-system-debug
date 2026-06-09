<script setup lang="ts">
const props = defineProps<{
  url?: string
  title?: string
}>()

const copied = ref(false)

const pageUrl = computed(() => props.url || (import.meta.client ? window.location.href : ''))
const pageTitle = computed(() => props.title || (import.meta.client ? document.title : ''))

const SHARES = [
  {
    id: 'twitter',
    label: 'X / Twitter',
    color: '#000',
    bg: '#f1f1f1',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.261 5.635 5.903-5.635Zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    href: (u: string, t: string) => `https://twitter.com/intent/tweet?text=${encodeURIComponent(t)}&url=${encodeURIComponent(u)}`,
  },
  {
    id: 'facebook',
    label: 'Facebook',
    color: '#1877f2',
    bg: '#e7f0fd',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073c0 6.03 4.388 11.024 10.125 11.927v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.269h3.328l-.532 3.49h-2.796v8.437C19.612 23.097 24 18.103 24 12.073z"/></svg>`,
    href: (u: string) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(u)}`,
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    color: '#0a66c2',
    bg: '#e8f0f9',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>`,
    href: (u: string) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(u)}`,
  },
  {
    id: 'whatsapp',
    label: 'WhatsApp',
    color: '#25d366',
    bg: '#eafaf1',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>`,
    href: (u: string, t: string) => `https://wa.me/?text=${encodeURIComponent(t + ' ' + u)}`,
  },
  {
    id: 'telegram',
    label: 'Telegram',
    color: '#26a5e4',
    bg: '#e8f5fd',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>`,
    href: (u: string, t: string) => `https://t.me/share/url?url=${encodeURIComponent(u)}&text=${encodeURIComponent(t)}`,
  },
  {
    id: 'email',
    label: 'Email',
    color: '#4b5563',
    bg: '#f1f5f9',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-4 w-4"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>`,
    href: (u: string, t: string) => `mailto:?subject=${encodeURIComponent(t)}&body=${encodeURIComponent(u)}`,
  },
]

const hovered = ref<string | null>(null)

async function share(s: typeof SHARES[number]) {
  if (s.id === 'email') {
    window.location.href = s.href(pageUrl.value, pageTitle.value)
    return
  }
  window.open(s.href(pageUrl.value, pageTitle.value), '_blank', 'noopener,width=640,height=480')
}

async function copyLink() {
  if (!import.meta.client) return
  await navigator.clipboard.writeText(pageUrl.value).catch(() => {})
  copied.value = true
  setTimeout(() => { copied.value = false }, 2500)
}

const canNativeShare = computed(() => import.meta.client && 'share' in navigator)

async function nativeShare() {
  try {
    await navigator.share({ title: pageTitle.value, url: pageUrl.value })
  } catch { /* cancelled */ }
}
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white px-5 py-4">
    <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Share this article</p>
    <div class="flex flex-wrap gap-2">
      <!-- Native share (mobile) -->
      <button
        v-if="canNativeShare"
        class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
        @click="nativeShare"
      >
        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13"/>
        </svg>
        Share
      </button>

      <!-- Platform buttons -->
      <button
        v-for="s in SHARES"
        :key="s.id"
        class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-all"
        :style="hovered === s.id ? { borderColor: s.color, color: s.color, background: s.bg } : {}"
        :title="s.label"
        @mouseenter="hovered = s.id"
        @mouseleave="hovered = null"
        @click="share(s)"
        v-html="s.icon"
      />

      <!-- Copy link -->
      <button
        class="flex h-8 items-center gap-1.5 rounded-lg border px-2.5 text-xs font-medium transition-all"
        :class="copied ? 'border-emerald-300 bg-emerald-50 text-emerald-700' : 'border-slate-200 text-slate-500 hover:bg-slate-50'"
        title="Copy link"
        @click="copyLink"
      >
        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
        </svg>
        {{ copied ? 'Copied!' : 'Copy link' }}
      </button>
    </div>
  </div>
</template>
