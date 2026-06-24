<script setup lang="ts">
import type { SourceType, CitationStyle, CitationData, Author } from '~/composables/useCitationFormatter'

useSeoMeta({
  title: 'Free Citation Generator — 10 Styles: APA, MLA, Chicago, Harvard & More | GradeCrest',
  description: 'Generate perfectly formatted citations in 10 styles — APA 7th, APA 6th, MLA 9th, Chicago, Harvard, Vancouver, AMA, ASA, IEEE, and Turabian. Supports books, journals, websites, chapters, newspapers, and YouTube. Free, instant, no sign-up.',
})

const { format } = useCitationFormatter()
const { lookupDOI, lookupISBN, lookupURL } = useLookup()

// ── Lookup state ───────────────────────────────────────────────────────────
const lookupTab    = ref<'doi' | 'isbn' | 'url'>('doi')
const lookupInput  = ref('')
const lookupStatus = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const lookupMsg    = ref('')
const lookupSource = ref('')

const lookupPlaceholder = computed(() => ({
  doi:  '10.1016/j.example.2023.01.001',
  isbn: '978-0-06-112008-4',
  url:  'https://example.com/article',
})[lookupTab.value])

async function runLookup() {
  lookupStatus.value = 'loading'
  lookupMsg.value    = ''
  try {
    const fn = lookupTab.value === 'doi' ? lookupDOI
             : lookupTab.value === 'isbn' ? lookupISBN
             : lookupURL
    const result = await fn(lookupInput.value)
    // Apply result to form
    sourceType.value = result.sourceType
    authors.value    = result.authors.length ? result.authors : [{ first: '', last: '' }]
    Object.assign(fields, result.fields)
    lookupSource.value = result.source
    lookupStatus.value = 'success'
    lookupMsg.value    = `Fields auto-filled from ${result.source}`
  } catch (err: any) {
    lookupStatus.value = 'error'
    lookupMsg.value    = err?.message ?? 'Lookup failed. Fill in fields manually.'
  }
}

// ── State ──────────────────────────────────────────────────────────────────
const sourceType = ref<SourceType>('book')
const style = ref<CitationStyle>('apa7')
const copied = ref(false)

const authors = ref<Author[]>([{ first: '', last: '' }])
const editors = ref<Author[]>([{ first: '', last: '' }])

const fields = reactive<Omit<CitationData, 'sourceType' | 'authors' | 'editors'>>({
  year: '', month: '', day: '',
  title: '', containerTitle: '',
  publisher: '', edition: '', volume: '', issue: '', pages: '',
  doi: '', url: '',
  accessYear: '', accessMonth: '', accessDay: '',
  location: '',
})

// ── Source type config ─────────────────────────────────────────────────────
const sourceTypes = [
  { value: 'book',      label: 'Book',           icon: '📖' },
  { value: 'journal',   label: 'Journal Article', icon: '🔬' },
  { value: 'website',   label: 'Website',         icon: '🌐' },
  { value: 'chapter',   label: 'Book Chapter',    icon: '📄' },
  { value: 'newspaper', label: 'Newspaper',       icon: '📰' },
  { value: 'youtube',   label: 'YouTube',         icon: '▶️' },
] as const

const styles = [
  { value: 'apa7',      label: 'APA 7th',      badge: 'Most popular' },
  { value: 'apa6',      label: 'APA 6th',       badge: '' },
  { value: 'mla9',      label: 'MLA 9th',       badge: '' },
  { value: 'chicago',   label: 'Chicago 17th',  badge: '' },
  { value: 'turabian',  label: 'Turabian 9th',  badge: '' },
  { value: 'harvard',   label: 'Harvard',        badge: '' },
  { value: 'ieee',      label: 'IEEE',           badge: '' },
  { value: 'vancouver', label: 'Vancouver',      badge: 'Medical' },
  { value: 'ama',       label: 'AMA 11th',       badge: 'Medical' },
  { value: 'asa',       label: 'ASA 6th',        badge: 'Sociology' },
] as const

const months = [
  { value: '',   label: 'Month' },
  { value: '1',  label: 'January' }, { value: '2',  label: 'February' },
  { value: '3',  label: 'March' },   { value: '4',  label: 'April' },
  { value: '5',  label: 'May' },     { value: '6',  label: 'June' },
  { value: '7',  label: 'July' },    { value: '8',  label: 'August' },
  { value: '9',  label: 'September' },{ value: '10', label: 'October' },
  { value: '11', label: 'November' },{ value: '12', label: 'December' },
]

// ── Field visibility ───────────────────────────────────────────────────────
const showEditors      = computed(() => sourceType.value === 'chapter')
const showTitle        = computed(() => true)
const showContainerTitle = computed(() => sourceType.value !== 'book')
const showPublisher    = computed(() => ['book', 'chapter'].includes(sourceType.value))
const showEdition      = computed(() => sourceType.value === 'book')
const showVolume       = computed(() => sourceType.value === 'journal')
const showIssue        = computed(() => sourceType.value === 'journal')
const showPages        = computed(() => ['journal', 'chapter', 'newspaper'].includes(sourceType.value))
const showDoi          = computed(() => ['book', 'journal', 'chapter'].includes(sourceType.value))
const showUrl          = computed(() => ['website', 'newspaper', 'youtube'].includes(sourceType.value))
const showDate         = computed(() => ['website', 'newspaper', 'youtube'].includes(sourceType.value))
const showAccessDate   = computed(() => sourceType.value === 'website')
const showLocation     = computed(() => false) // hidden; used internally for Chicago
const titleLabel       = computed(() => {
  if (sourceType.value === 'journal') return 'Article Title'
  if (sourceType.value === 'chapter') return 'Chapter Title'
  if (sourceType.value === 'newspaper') return 'Article Title'
  if (sourceType.value === 'youtube') return 'Video Title'
  return 'Title'
})
const containerLabel   = computed(() => {
  if (sourceType.value === 'journal') return 'Journal Name'
  if (sourceType.value === 'chapter') return 'Book Title'
  if (sourceType.value === 'newspaper') return 'Newspaper Name'
  if (sourceType.value === 'website') return 'Site Name'
  if (sourceType.value === 'youtube') return 'Channel Name'
  return 'Container'
})

// ── Author helpers ─────────────────────────────────────────────────────────
function addAuthor() {
  if (authors.value.length < 20) authors.value.push({ first: '', last: '' })
}
function removeAuthor(i: number) {
  if (authors.value.length > 1) authors.value.splice(i, 1)
}
function addEditor() {
  if (editors.value.length < 10) editors.value.push({ first: '', last: '' })
}
function removeEditor(i: number) {
  if (editors.value.length > 1) editors.value.splice(i, 1)
}

// ── Computed citation data ─────────────────────────────────────────────────
const citationData = computed<CitationData>(() => ({
  sourceType: sourceType.value,
  authors: authors.value,
  editors: editors.value,
  ...fields,
}))

const citation = computed(() => format(style.value, citationData.value))

const allStyleCitations = computed(() =>
  (['apa7', 'apa6', 'mla9', 'chicago', 'turabian', 'harvard', 'ieee', 'vancouver', 'ama', 'asa'] as CitationStyle[]).map(s => ({
    label: styles.find(x => x.value === s)?.label ?? s,
    text: format(s, citationData.value),
  }))
)

// ── Render helper: *text* → <em>text</em> ─────────────────────────────────
function renderCitation(text: string): string {
  return text.replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

// ── Clipboard ─────────────────────────────────────────────────────────────
async function copyToClipboard() {
  const plain = citation.value.replace(/\*([^*]+)\*/g, '$1')
  await navigator.clipboard.writeText(plain)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function clearForm() {
  authors.value = [{ first: '', last: '' }]
  editors.value = [{ first: '', last: '' }]
  Object.assign(fields, {
    year: '', month: '', day: '',
    title: '', containerTitle: '',
    publisher: '', edition: '', volume: '', issue: '', pages: '',
    doi: '', url: '',
    accessYear: '', accessMonth: '', accessDay: '',
    location: '',
  })
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-6xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Citation Generator</span>
      </nav>
    </div>

    <div class="max-w-6xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Citation Generator</h1>
      <p class="text-slate-500 text-sm">Generates perfectly formatted references in <strong>10 citation styles</strong> — APA 7th, MLA 9th, Chicago 17th, Harvard, Vancouver, and more. Updates live as you type. Free, no sign-up.</p>
      <div class="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-3">
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>
          No sign-up required
        </span>
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>
          Updates as you type
        </span>
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>
          10 citation styles
        </span>
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>
          6 source types
        </span>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-4 pb-16 flex flex-col lg:flex-row gap-6">
      <!-- ── Left: Form ── -->
      <div class="flex-1 space-y-6 min-w-0">

        <!-- Quick Lookup -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <div class="flex items-center gap-2 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-brand-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 15.803m10.607 0A7.5 7.5 0 0 0 5.196 15.803"/></svg>
            <h2 class="text-sm font-bold text-slate-700">Quick Lookup <span class="text-xs font-normal text-slate-400 ml-1">— paste a DOI, ISBN, or URL to auto-fill</span></h2>
          </div>
          <!-- Tabs -->
          <div class="flex gap-1 mb-3 rounded-xl bg-slate-100 p-1 w-fit">
            <button
              v-for="tab in (['doi', 'isbn', 'url'] as const)"
              :key="tab"
              type="button"
              @click="lookupTab = tab; lookupStatus = 'idle'; lookupInput = ''"
              class="rounded-lg px-4 py-1.5 text-xs font-bold transition-all uppercase tracking-wide"
              :class="lookupTab === tab ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            >{{ tab }}</button>
          </div>
          <!-- Input + button -->
          <div class="flex gap-2">
            <input
              v-model="lookupInput"
              type="text"
              :placeholder="lookupPlaceholder"
              class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              @keydown.enter.prevent="runLookup"
            />
            <button
              type="button"
              :disabled="lookupStatus === 'loading'"
              @click="runLookup"
              class="rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60 transition-colors flex items-center gap-2 shrink-0"
            >
              <svg v-if="lookupStatus === 'loading'" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              {{ lookupStatus === 'loading' ? 'Looking up…' : 'Look up' }}
            </button>
          </div>
          <!-- Status messages -->
          <p v-if="lookupStatus === 'success'" class="mt-2.5 flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
            <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>
            {{ lookupMsg }}
          </p>
          <p v-else-if="lookupStatus === 'error'" class="mt-2.5 flex items-center gap-1.5 text-xs font-semibold text-red-500">
            <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
            {{ lookupMsg }}
          </p>
        </div>

        <!-- Step 1: Source Type -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">1. Source Type</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button
              v-for="st in sourceTypes"
              :key="st.value"
              type="button"
              @click="sourceType = st.value"
              :class="[
                'flex flex-col items-center gap-1.5 rounded-xl border-2 px-3 py-3 text-xs font-semibold transition-all',
                sourceType === st.value
                  ? 'border-brand-500 bg-brand-50 text-brand-700'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:bg-slate-50'
              ]"
            >
              <span class="text-xl">{{ st.icon }}</span>
              {{ st.label }}
            </button>
          </div>
        </div>

        <!-- Step 2: Citation Style -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">2. Citation Style</h2>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="s in styles"
              :key="s.value"
              type="button"
              @click="style = s.value"
              :class="[
                'rounded-full border px-3 py-1.5 text-xs font-semibold transition-all flex items-center gap-1',
                style === s.value
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:bg-slate-50'
              ]"
            >
              {{ s.label }}
              <span
                v-if="s.badge"
                class="rounded-full px-1.5 py-0.5 text-[10px] font-bold"
                :class="style === s.value ? 'bg-white/20 text-white' : 'bg-brand-100 text-brand-600'"
              >{{ s.badge }}</span>
            </button>
          </div>
        </div>

        <!-- Step 3: Fields -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider">3. Source Details</h2>

          <!-- Authors -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              {{ sourceType === 'youtube' ? 'Channel / Author' : 'Author(s)' }}
            </label>
            <div class="space-y-2">
              <div v-for="(author, i) in authors" :key="i" class="flex gap-2 items-center">
                <input
                  v-model="author.first"
                  type="text"
                  placeholder="First name"
                  class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                />
                <input
                  v-model="author.last"
                  type="text"
                  placeholder="Last name"
                  class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                />
                <button
                  v-if="authors.length > 1"
                  type="button"
                  @click="removeAuthor(i)"
                  class="text-slate-400 hover:text-red-500 transition-colors flex-shrink-0"
                  aria-label="Remove author"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
            </div>
            <button
              v-if="authors.length < 20"
              type="button"
              @click="addAuthor"
              class="mt-2 text-sm text-brand-600 font-semibold hover:text-brand-700 transition-colors flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
              Add author
            </button>
          </div>

          <!-- Editors (chapter only) -->
          <div v-if="showEditors">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Editor(s)</label>
            <div class="space-y-2">
              <div v-for="(editor, i) in editors" :key="i" class="flex gap-2 items-center">
                <input
                  v-model="editor.first"
                  type="text"
                  placeholder="First name"
                  class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                />
                <input
                  v-model="editor.last"
                  type="text"
                  placeholder="Last name"
                  class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                />
                <button
                  v-if="editors.length > 1"
                  type="button"
                  @click="removeEditor(i)"
                  class="text-slate-400 hover:text-red-500 transition-colors flex-shrink-0"
                  aria-label="Remove editor"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
            </div>
            <button
              v-if="editors.length < 10"
              type="button"
              @click="addEditor"
              class="mt-2 text-sm text-brand-600 font-semibold hover:text-brand-700 transition-colors flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
              Add editor
            </button>
          </div>

          <!-- Title -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              {{ titleLabel }} <span class="text-red-400">*</span>
            </label>
            <input
              v-model="fields.title"
              type="text"
              :placeholder="`Enter ${titleLabel.toLowerCase()}`"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <!-- Container title -->
          <div v-if="showContainerTitle">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              {{ containerLabel }}
            </label>
            <input
              v-model="fields.containerTitle"
              type="text"
              :placeholder="`Enter ${containerLabel.toLowerCase()}`"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <!-- Publisher + Edition row -->
          <div class="flex gap-3 flex-wrap">
            <div v-if="showPublisher" class="flex-1 min-w-36">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Publisher <span class="text-red-400">*</span></label>
              <input
                v-model="fields.publisher"
                type="text"
                placeholder="Publisher name"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <div v-if="showEdition" class="w-28">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Edition</label>
              <input
                v-model="fields.edition"
                type="text"
                placeholder="e.g. 3"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
          </div>

          <!-- Volume + Issue + Pages row -->
          <div v-if="showVolume || showIssue || showPages" class="flex gap-3 flex-wrap">
            <div v-if="showVolume" class="flex-1 min-w-24">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Volume</label>
              <input
                v-model="fields.volume"
                type="text"
                placeholder="e.g. 12"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <div v-if="showIssue" class="flex-1 min-w-24">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Issue</label>
              <input
                v-model="fields.issue"
                type="text"
                placeholder="e.g. 3"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <div v-if="showPages" class="flex-1 min-w-32">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Pages</label>
              <input
                v-model="fields.pages"
                type="text"
                placeholder="e.g. 45–67"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
          </div>

          <!-- Year + Date row -->
          <div class="flex gap-3 flex-wrap">
            <div class="w-28">
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Year <span class="text-red-400">*</span></label>
              <input
                v-model="fields.year"
                type="text"
                placeholder="2024"
                maxlength="4"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <template v-if="showDate">
              <div class="flex-1 min-w-32">
                <label class="block text-sm font-semibold text-slate-700 mb-1.5">Month</label>
                <select
                  v-model="fields.month"
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                >
                  <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
                </select>
              </div>
              <div class="w-20">
                <label class="block text-sm font-semibold text-slate-700 mb-1.5">Day</label>
                <input
                  v-model="fields.day"
                  type="text"
                  placeholder="12"
                  maxlength="2"
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
                />
              </div>
            </template>
          </div>

          <!-- Access date (website only) -->
          <div v-if="showAccessDate">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Access Date</label>
            <div class="flex gap-3 flex-wrap">
              <input
                v-model="fields.accessYear"
                type="text"
                placeholder="Year"
                maxlength="4"
                class="w-24 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
              <select
                v-model="fields.accessMonth"
                class="flex-1 min-w-32 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              >
                <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
              <input
                v-model="fields.accessDay"
                type="text"
                placeholder="Day"
                maxlength="2"
                class="w-20 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
          </div>

          <!-- DOI -->
          <div v-if="showDoi">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">DOI <span class="text-slate-400 font-normal text-xs">(optional)</span></label>
            <input
              v-model="fields.doi"
              type="text"
              placeholder="10.1234/example"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <!-- URL -->
          <div v-if="showUrl || (!showDoi && sourceType !== 'book')">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              URL
              <span v-if="['website','youtube'].includes(sourceType)" class="text-red-400">*</span>
              <span v-else class="text-slate-400 font-normal text-xs">(optional)</span>
            </label>
            <input
              v-model="fields.url"
              type="url"
              placeholder="https://..."
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
        </div>
      </div>

      <!-- ── Right: Output ── -->
      <div class="lg:w-96 xl:w-[440px] flex-shrink-0 space-y-5">

        <!-- Citation output -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 sticky top-24">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Your Citation</h2>

          <div class="rounded-xl bg-slate-50 border border-slate-200 p-4 min-h-24 text-sm text-slate-800 leading-relaxed font-serif" v-html="renderCitation(citation)" />

          <div class="flex gap-2 mt-4">
            <button
              type="button"
              @click="copyToClipboard"
              class="flex-1 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/></svg>
              {{ copied ? 'Copied!' : 'Copy citation' }}
            </button>
            <button
              type="button"
              @click="clearForm"
              class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Clear
            </button>
          </div>

          <!-- All styles table -->
          <div class="mt-6">
            <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Your source in all 10 styles</h3>
            <div class="space-y-3 max-h-96 overflow-y-auto pr-1">
              <div
                v-for="s in allStyleCitations"
                :key="s.label"
                class="text-xs"
              >
                <span class="inline-block font-bold text-brand-700 mb-0.5">{{ s.label }}</span>
                <p class="text-slate-600 leading-relaxed font-serif" v-html="renderCitation(s.text)" />
              </div>
            </div>
          </div>
        </div>

        <!-- CTA -->
        <div class="rounded-2xl bg-brand-50 border border-brand-100 p-5 text-center">
          <p class="text-sm text-slate-600 mb-3">Need help writing your paper? Our experts write custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
          <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
            Order a paper →
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
