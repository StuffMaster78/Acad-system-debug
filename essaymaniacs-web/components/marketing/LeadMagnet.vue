<script setup lang="ts">
interface Props {
  attachmentSlug: string
  title?: string
  description?: string
  variant?: 'inline' | 'card'
}

const props = withDefaults(defineProps<Props>(), { variant: 'inline' })

const config  = useRuntimeConfig()
const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

// Fetch attachment metadata if title not supplied via props
interface AttachmentMeta {
  title: string
  description: string
  gate_type: string
}

const { data: meta } = await useAsyncData<AttachmentMeta | null>(
  `attachment-meta-${props.attachmentSlug}`,
  async () => {
    if (!apiBase || (props.title && props.description)) return null
    try {
      const res = await $fetch<{ items?: AttachmentMeta[] }>(`${apiBase}/cms-api/attachments/`, {
        query: { slug: props.attachmentSlug },
      })
      return res?.items?.[0] ?? null
    } catch { return null }
  },
)

const displayTitle       = computed(() => props.title       || meta.value?.title       || 'Free Cheat Sheet')
const displayDescription = computed(() => props.description || meta.value?.description || 'Enter your email to get the free download.')

// Form state
const email   = ref('')
const status  = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const message = ref('')

async function submit() {
  if (!email.value.trim() || !email.value.includes('@')) {
    status.value = 'error'
    message.value = 'Please enter a valid email address.'
    return
  }
  status.value = 'loading'
  try {
    await $fetch(`${apiBase}/cms-api/attachments/${props.attachmentSlug}/download/`, {
      method: 'POST',
      body: { email: email.value.trim(), consent_marketing: true },
    })
    status.value = 'success'
    message.value = 'Check your inbox — your download link is on its way!'
  } catch (err: any) {
    status.value = 'error'
    message.value = err?.data?.error || 'Something went wrong. Please try again.'
  }
}
</script>

<template>
  <!-- Inline variant (mid-article, full-width) -->
  <div
    v-if="variant === 'inline'"
    class="rounded-2xl border-l-4 border-brand-500 bg-brand-50 p-5 sm:p-6"
  >
    <div class="flex items-start gap-4">
      <!-- Icon -->
      <div class="hidden shrink-0 sm:flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100">
        <svg class="h-6 w-6 text-brand-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
        </svg>
      </div>

      <div class="flex-1 min-w-0">
        <p class="text-[10px] font-bold uppercase tracking-widest text-brand-600 mb-0.5">Free Download</p>
        <p class="text-base font-bold text-slate-900 leading-snug">{{ displayTitle }}</p>
        <p class="mt-1 text-sm text-slate-600 leading-relaxed">{{ displayDescription }}</p>

        <!-- Success state -->
        <div v-if="status === 'success'" class="mt-4 flex items-center gap-2 text-sm font-semibold text-emerald-600">
          <svg class="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
          </svg>
          {{ message }}
        </div>

        <!-- Form -->
        <form v-else class="mt-4 flex flex-col gap-2 sm:flex-row sm:items-start" @submit.prevent="submit">
          <input
            v-model="email"
            type="email"
            placeholder="your@email.com"
            required
            class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
          <button
            type="submit"
            :disabled="status === 'loading'"
            class="shrink-0 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60 transition-colors flex items-center gap-2"
          >
            <svg v-if="status === 'loading'" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            {{ status === 'loading' ? 'Sending…' : 'Get it free →' }}
          </button>
        </form>

        <p v-if="status === 'error'" class="mt-1.5 text-xs text-red-500">{{ message }}</p>
        <p v-else class="mt-1.5 text-xs text-slate-400">Sent instantly. No spam, ever.</p>
      </div>
    </div>
  </div>

  <!-- Card variant (sidebar, compact) -->
  <div
    v-else
    class="rounded-2xl border border-brand-100 bg-brand-50 p-5"
  >
    <p class="text-[10px] font-bold uppercase tracking-widest text-brand-600 mb-1">Free Download</p>
    <p class="text-sm font-bold text-slate-900 leading-snug mb-1">{{ displayTitle }}</p>
    <p class="text-xs text-slate-500 leading-relaxed mb-3">{{ displayDescription }}</p>

    <div v-if="status === 'success'" class="flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
      <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
      </svg>
      Check your inbox!
    </div>
    <form v-else class="space-y-2" @submit.prevent="submit">
      <input
        v-model="email"
        type="email"
        placeholder="your@email.com"
        required
        class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
      />
      <button
        type="submit"
        :disabled="status === 'loading'"
        class="w-full rounded-xl bg-brand-600 py-2 text-xs font-bold text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
      >
        {{ status === 'loading' ? 'Sending…' : 'Send me the PDF →' }}
      </button>
      <p v-if="status === 'error'" class="text-[10px] text-red-500">{{ message }}</p>
    </form>
  </div>
</template>
