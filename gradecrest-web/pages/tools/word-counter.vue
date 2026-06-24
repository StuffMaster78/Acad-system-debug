<script setup lang="ts">
useSeoMeta({
  title: 'Free Word Counter — Count Words, Characters & Reading Time',
  description: 'Real-time word counter, character counter, sentence counter and reading time calculator. Paste your text and get instant stats. No sign-up required.',
})

const STOP_WORDS = new Set([
  'the','a','an','and','or','but','in','on','at','to','for','of','is','it',
  'this','that','was','are','be','been','with','as','by','from','he','she',
  'they','we','you','i','my','your','his','her','our','their','its','me',
  'him','us','them','what','which','who','whom','when','where','why','how',
  'all','each','every','both','few','more','most','other','some','such',
  'no','not','only','same','so','than','too','very','just','can','will',
  'do','did','does','had','has','have','may','would','should','could',
  'into','up','out','about','after','before','between','through','over',
  'then','there','here','if','else','any','these','those','am','were',
  'been','being','get','got','let','set','go','went','come','came',
])

const text = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const wordCount = computed(() => {
  const m = text.value.trim().match(/\S+/g)
  return m ? m.length : 0
})
const charCount = computed(() => text.value.length)
const charNoSpaces = computed(() => text.value.replace(/\s/g, '').length)
const sentenceCount = computed(() => {
  const m = text.value.match(/[^.!?]*[.!?]+/g)
  return m ? m.filter(s => s.trim().length > 0).length : 0
})
const paragraphCount = computed(() => {
  if (!text.value.trim()) return 0
  return text.value.split(/\n\s*\n/).filter(p => p.trim().length > 0).length
})
const readingTime = computed(() => {
  const totalSec = Math.round((wordCount.value / 200) * 60)
  return { min: Math.floor(totalSec / 60), sec: totalSec % 60 }
})
const speakingTime = computed(() => {
  const totalSec = Math.round((wordCount.value / 130) * 60)
  return { min: Math.floor(totalSec / 60), sec: totalSec % 60 }
})

function formatTime(t: { min: number; sec: number }) {
  if (t.min === 0 && t.sec === 0) return '0 sec'
  if (t.min === 0) return `${t.sec} sec`
  if (t.sec === 0) return `${t.min} min`
  return `${t.min} min ${t.sec} sec`
}

const topWords = computed(() => {
  if (!text.value.trim()) return []
  const words = text.value.toLowerCase().replace(/[^a-z0-9\s'-]/g, '').split(/\s+/).filter(w => w.length > 2 && !STOP_WORDS.has(w))
  const freq: Record<string, number> = {}
  for (const w of words) freq[w] = (freq[w] ?? 0) + 1
  return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 10)
})

const avgWordsPerSentence = computed(() => {
  if (sentenceCount.value === 0) return 0
  return Math.round(wordCount.value / sentenceCount.value)
})
const avgCharsPerWord = computed(() => {
  if (wordCount.value === 0) return 0
  return (charNoSpaces.value / wordCount.value).toFixed(1)
})
const readabilityLabel = computed(() => {
  const avg = avgWordsPerSentence.value
  if (avg === 0) return null
  if (avg < 15) return { label: 'Easy', color: 'text-green-600 bg-green-50 border-green-200' }
  if (avg <= 20) return { label: 'Moderate', color: 'text-amber-600 bg-amber-50 border-amber-200' }
  return { label: 'Complex', color: 'text-red-600 bg-red-50 border-red-200' }
})

function clearText() { text.value = '' }

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { text.value = ev.target?.result as string ?? '' }
  reader.readAsText(file)
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Word Counter</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Word Counter</h1>
      <p class="text-slate-500 text-sm">Paste or type your text to get real-time word, character, and reading time statistics.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Stats grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-3xl font-extrabold text-brand-600">{{ wordCount.toLocaleString() }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Words</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-3xl font-extrabold text-slate-700">{{ charCount.toLocaleString() }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Characters</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-3xl font-extrabold text-slate-700">{{ charNoSpaces.toLocaleString() }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Chars (no spaces)</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-3xl font-extrabold text-slate-700">{{ sentenceCount.toLocaleString() }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Sentences</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-3xl font-extrabold text-slate-700">{{ paragraphCount.toLocaleString() }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Paragraphs</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-xl font-extrabold text-slate-700">{{ formatTime(readingTime) }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Reading time</p>
        </div>
        <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-xl font-extrabold text-slate-700">{{ formatTime(speakingTime) }}</p>
          <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Speaking time</p>
        </div>
        <div v-if="readabilityLabel" class="rounded-2xl border shadow-sm p-4 text-center" :class="readabilityLabel.color">
          <p class="text-2xl font-extrabold">{{ readabilityLabel.label }}</p>
          <p class="text-xs font-semibold mt-1 uppercase tracking-wide opacity-80">Readability</p>
        </div>
        <div v-else class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
          <p class="text-2xl font-extrabold text-slate-300">—</p>
          <p class="text-xs font-semibold text-slate-400 mt-1 uppercase tracking-wide">Readability</p>
        </div>
      </div>

      <!-- Textarea -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <label class="text-sm font-bold text-slate-700">Your Text</label>
          <div class="flex items-center gap-3">
            <span class="text-xs text-slate-400">{{ charCount.toLocaleString() }} / no limit</span>
            <label class="cursor-pointer text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/></svg>
              Upload .txt
              <input ref="fileInput" type="file" accept=".txt" class="hidden" @change="onFileChange" />
            </label>
            <button v-if="text" type="button" @click="clearText" class="text-xs font-semibold text-slate-500 hover:text-red-500 transition-colors flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              Clear
            </button>
          </div>
        </div>
        <textarea
          v-model="text"
          placeholder="Paste or type your text here…"
          class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-y leading-relaxed"
          style="min-height: 300px;"
        />
      </div>

      <!-- Top words -->
      <div v-if="topWords.length > 0" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-700 mb-4">Top 10 Most Frequent Words</h2>
        <!-- Bar chart -->
        <div class="space-y-2 mb-5">
          <div v-for="([word, count], i) in topWords" :key="word" class="flex items-center gap-3">
            <span class="text-xs text-slate-500 w-4 text-right flex-shrink-0">{{ i + 1 }}</span>
            <span class="text-xs font-semibold text-slate-700 w-24 flex-shrink-0 truncate">{{ word }}</span>
            <div class="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                class="h-full rounded-full bg-brand-500 transition-all"
                :style="{ width: `${(count / topWords[0][1]) * 100}%` }"
              />
            </div>
            <span class="text-xs font-bold text-brand-600 w-8 text-right flex-shrink-0">{{ count }}</span>
          </div>
        </div>
        <!-- Pill chips -->
        <div class="flex flex-wrap gap-2">
          <span
            v-for="([word, count]) in topWords"
            :key="word + '-pill'"
            class="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 border border-brand-100"
          >
            {{ word }}
            <span class="bg-brand-600 text-white rounded-full px-1.5 py-0.5 text-[10px] font-bold leading-none">{{ count }}</span>
          </span>
        </div>
      </div>

      <!-- Readability details -->
      <div v-if="wordCount > 0" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-700 mb-4">Readability Details</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-2xl font-extrabold text-slate-700">{{ avgWordsPerSentence }}</p>
            <p class="text-xs text-slate-500 mt-1">Avg words / sentence</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-extrabold text-slate-700">{{ avgCharsPerWord }}</p>
            <p class="text-xs text-slate-500 mt-1">Avg chars / word</p>
          </div>
          <div v-if="readabilityLabel" class="text-center">
            <span class="inline-flex items-center rounded-full border px-4 py-1 text-sm font-bold" :class="readabilityLabel.color">
              {{ readabilityLabel.label }}
            </span>
            <p class="text-xs text-slate-500 mt-2">
              {{ avgWordsPerSentence < 15 ? '< 15 words/sentence' : avgWordsPerSentence <= 20 ? '15–20 words/sentence' : '> 20 words/sentence' }}
            </p>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full essay written by experts? We deliver custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
