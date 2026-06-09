<script setup lang="ts">
/**
 * SampleDownload — PDF/file download card with full gating support.
 *
 * Gate types (from cms_attachments.Attachment.gate_type):
 *   free      → direct download, no barrier
 *   email     → collect email, then download
 *   account   → must be logged in
 *   customer  → must have placed at least one order
 *   paid      → must purchase before downloading
 */

interface AttachmentMeta {
  slug: string
  title: string
  description?: string
  file_format?: string        // 'pdf', 'docx', etc.
  file_size_bytes?: number
  page_count?: number
  academic_level?: string
  formatting_style?: string
  word_count?: number
  gate_type: 'free' | 'email' | 'account' | 'customer' | 'paid'
  price?: string | null
  preview_url?: string        // thumbnail / first-page image
}

const props = defineProps<{
  attachment: AttachmentMeta
  /** Visual variant: 'card' (default), 'compact', 'hero' */
  variant?: 'card' | 'compact' | 'hero'
}>()

// ── State ─────────────────────────────────────────────────────────────────
const state = ref<'idle' | 'checking' | 'email-form' | 'downloading' | 'done' | 'error'>('idle')
const email = ref('')
const emailError = ref('')
const downloadUrl = ref('')
const errorMsg = ref('')

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || ''

// ── Helpers ───────────────────────────────────────────────────────────────
function fmtSize(bytes?: number): string {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const FORMAT_LABEL: Record<string, string> = {
  pdf: 'PDF', docx: 'Word', xlsx: 'Excel', pptx: 'PowerPoint',
}

const LEVEL_LABEL: Record<string, string> = {
  high_school: 'High School', undergraduate: 'Undergraduate',
  graduate: 'Graduate', phd: 'PhD', general: 'General',
}

const GATE_LABEL: Record<string, string> = {
  free: 'Free download',
  email: 'Free — email required',
  account: 'Account required',
  customer: 'Customers only',
  paid: props.attachment.price ? `$${props.attachment.price}` : 'Paid',
}

const buttonLabel = computed(() => {
  if (state.value === 'checking') return 'Checking…'
  if (state.value === 'downloading') return 'Preparing download…'
  if (state.value === 'done') return '✓ Downloaded'
  if (props.attachment.gate_type === 'paid') return props.attachment.price ? `Purchase — $${props.attachment.price}` : 'Purchase'
  if (props.attachment.gate_type === 'account' || props.attachment.gate_type === 'customer') return 'Sign in to download'
  return 'Download'
})

// ── Actions ───────────────────────────────────────────────────────────────
async function handleClick() {
  if (state.value === 'done') return
  if (props.attachment.gate_type === 'account' || props.attachment.gate_type === 'customer') {
    navigateTo('/login?redirect=' + encodeURIComponent(window.location.pathname))
    return
  }
  if (props.attachment.gate_type === 'paid') {
    navigateTo('/order')
    return
  }

  state.value = 'checking'
  errorMsg.value = ''

  try {
    const access = await $fetch<{
      allowed: boolean
      requires_email?: boolean
      reason?: string
    }>(`${apiBase}/cms-api/attachments/${props.attachment.slug}/check_access/`)

    if (access.allowed) {
      await doDownload()
    } else if (access.requires_email) {
      state.value = 'email-form'
    } else {
      state.value = 'error'
      errorMsg.value = access.reason || 'Access denied.'
    }
  } catch {
    state.value = 'error'
    errorMsg.value = 'Could not reach the server. Please try again.'
  }
}

async function submitEmail() {
  emailError.value = ''
  if (!email.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    emailError.value = 'Please enter a valid email address.'
    return
  }
  await doDownload(email.value)
}

async function doDownload(emailVal?: string) {
  state.value = 'downloading'
  try {
    const result = await $fetch<{ download_url?: string; error?: string }>(
      `${apiBase}/cms-api/attachments/${props.attachment.slug}/download/`,
      { method: 'POST', body: emailVal ? { email: emailVal } : {} },
    )
    if (result.download_url) {
      downloadUrl.value = result.download_url
      state.value = 'done'
      // Trigger browser download
      const a = document.createElement('a')
      a.href = result.download_url
      a.download = props.attachment.title
      a.click()
    } else {
      state.value = 'error'
      errorMsg.value = result.error || 'Download failed.'
    }
  } catch {
    state.value = 'error'
    errorMsg.value = 'Download failed. Please try again.'
  }
}
</script>

<template>
  <!-- ── Hero variant ──────────────────────────────────────────────────── -->
  <div
    v-if="variant === 'hero'"
    class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
  >
    <!-- Preview image -->
    <div v-if="attachment.preview_url" class="h-48 overflow-hidden bg-slate-100">
      <img :src="attachment.preview_url" :alt="attachment.title" class="h-full w-full object-cover" loading="lazy" />
    </div>
    <div v-else class="flex h-48 items-center justify-center bg-gradient-to-br from-brand-50 to-brand-100">
      <svg class="h-16 w-16 text-brand-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
      </svg>
    </div>
    <div class="p-6">
      <SampleDownload :attachment="attachment" variant="card" />
    </div>
  </div>

  <!-- ── Card + compact variants ───────────────────────────────────────── -->
  <div
    v-else
    class="overflow-hidden rounded-xl border border-slate-200 bg-white"
    :class="variant === 'compact' ? 'p-4' : 'p-5'"
  >
    <div class="flex items-start gap-4">
      <!-- File icon -->
      <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50">
        <svg class="h-6 w-6 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
      </div>

      <div class="min-w-0 flex-1">
        <!-- Title + gate badge -->
        <div class="flex flex-wrap items-start justify-between gap-2">
          <p class="font-semibold text-slate-900 leading-snug">{{ attachment.title }}</p>
          <span
            class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="{
              'bg-emerald-100 text-emerald-700': attachment.gate_type === 'free',
              'bg-blue-100 text-blue-700':       attachment.gate_type === 'email',
              'bg-brand-100 text-brand-700':     attachment.gate_type === 'account' || attachment.gate_type === 'customer',
              'bg-amber-100 text-amber-700':     attachment.gate_type === 'paid',
            }"
          >
            {{ GATE_LABEL[attachment.gate_type] }}
          </span>
        </div>

        <p v-if="attachment.description && variant !== 'compact'" class="mt-1 text-sm leading-5 text-slate-500">
          {{ attachment.description }}
        </p>

        <!-- Metadata pills -->
        <div class="mt-2 flex flex-wrap gap-1.5 text-[11px]">
          <span v-if="attachment.file_format" class="rounded bg-slate-100 px-1.5 py-0.5 font-semibold text-slate-600">
            {{ FORMAT_LABEL[attachment.file_format] ?? attachment.file_format.toUpperCase() }}
          </span>
          <span v-if="attachment.page_count" class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-500">
            {{ attachment.page_count }} pages
          </span>
          <span v-if="attachment.file_size_bytes" class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-500">
            {{ fmtSize(attachment.file_size_bytes) }}
          </span>
          <span v-if="attachment.academic_level && attachment.academic_level !== 'general'" class="rounded bg-brand-50 px-1.5 py-0.5 text-brand-600">
            {{ LEVEL_LABEL[attachment.academic_level] ?? attachment.academic_level }}
          </span>
          <span v-if="attachment.formatting_style && attachment.formatting_style !== 'na'" class="rounded bg-brand-50 px-1.5 py-0.5 text-brand-600 uppercase">
            {{ attachment.formatting_style }}
          </span>
        </div>
      </div>
    </div>

    <!-- Email form (shown when gate_type === 'email' and access check requires it) -->
    <div v-if="state === 'email-form'" class="mt-4 rounded-xl border border-brand-100 bg-brand-50 p-4">
      <p class="mb-3 text-sm font-medium text-slate-700">Enter your email to get the free download:</p>
      <div class="flex gap-2">
        <input
          v-model="email"
          type="email"
          placeholder="your@email.com"
          class="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          @keyup.enter="submitEmail"
        />
        <button
          class="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
          @click="submitEmail"
        >
          Send
        </button>
      </div>
      <p v-if="emailError" class="mt-1.5 text-xs text-rose-600">{{ emailError }}</p>
      <p class="mt-1.5 text-xs text-slate-400">We'll only use your email to send you the download link.</p>
    </div>

    <!-- Error message -->
    <p v-if="state === 'error'" class="mt-3 text-xs text-rose-600">{{ errorMsg }}</p>

    <!-- Download button -->
    <button
      v-if="state !== 'email-form'"
      class="mt-4 flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-semibold transition-all"
      :class="{
        'bg-brand-700 text-white hover:bg-brand-800': state === 'idle' && attachment.gate_type !== 'paid',
        'bg-amber-600 text-white hover:bg-amber-700': state === 'idle' && attachment.gate_type === 'paid',
        'bg-slate-100 text-slate-400 cursor-not-allowed': state === 'checking' || state === 'downloading',
        'bg-emerald-100 text-emerald-700 cursor-default': state === 'done',
        'bg-rose-50 text-rose-600': state === 'error',
      }"
      :disabled="state === 'checking' || state === 'downloading' || state === 'done'"
      @click="handleClick"
    >
      <!-- Spinner -->
      <svg v-if="state === 'checking' || state === 'downloading'" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <!-- Download icon -->
      <svg v-else-if="state === 'idle'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
      </svg>
      {{ buttonLabel }}
    </button>

    <!-- Paid disclaimer -->
    <p v-if="attachment.gate_type === 'paid' && state === 'idle'" class="mt-2 text-center text-xs text-slate-400">
      One-time purchase · Instant access · PDF download
    </p>
  </div>
</template>
