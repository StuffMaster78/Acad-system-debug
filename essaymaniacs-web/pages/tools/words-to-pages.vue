<script setup lang="ts">
useSeoMeta({
  title: 'Words to Pages Converter — Free Academic Writing Tool',
  description: 'Convert word count to pages or pages to words. Supports Times New Roman, Arial, Calibri, double-spacing, APA and MLA formatting. Free, instant, no sign-up.',
})

type Mode = 'words-to-pages' | 'pages-to-words'
type Font = 'Times New Roman' | 'Arial' | 'Calibri' | 'Courier New' | 'Georgia'
type Size = '10pt' | '11pt' | '12pt' | '14pt'
type Spacing = 'Single' | '1.5x' | 'Double'
type Margin = 'Normal (1")' | 'Narrow (0.5")' | 'Wide (1.5")'

const mode = ref<Mode>('words-to-pages')
const font = ref<Font>('Times New Roman')
const size = ref<Size>('12pt')
const spacing = ref<Spacing>('Double')
const margin = ref<Margin>('Normal (1")')

const wordInput = ref(500)
const pageInput = ref(2)

const fontMultipliers: Record<Font, number> = {
  'Times New Roman': 1.0,
  'Arial': 0.95,
  'Calibri': 0.97,
  'Courier New': 0.85,
  'Georgia': 0.92,
}
const sizeMultipliers: Record<Size, number> = {
  '10pt': 1.25,
  '11pt': 1.12,
  '12pt': 1.0,
  '14pt': 0.85,
}
const spacingMultipliers: Record<Spacing, number> = {
  'Single': 2.0,
  '1.5x': 1.33,
  'Double': 1.0,
}
const marginMultipliers: Record<Margin, number> = {
  'Normal (1")': 1.0,
  'Narrow (0.5")': 1.12,
  'Wide (1.5")': 0.88,
}

const wordsPerPage = computed(() =>
  Math.round(275 * fontMultipliers[font.value] * sizeMultipliers[size.value] * spacingMultipliers[spacing.value] * marginMultipliers[margin.value])
)

const pagesResult = computed(() => {
  if (wordInput.value <= 0) return 0
  return Math.round((wordInput.value / wordsPerPage.value) * 10) / 10
})
const singleSpacedPages = computed(() => {
  const wpp = Math.round(275 * fontMultipliers[font.value] * sizeMultipliers[size.value] * 2.0 * marginMultipliers[margin.value])
  return Math.round((wordInput.value / wpp) * 10) / 10
})
const wordsResult = computed(() => Math.round(pageInput.value * wordsPerPage.value))

const referenceWords = [250, 500, 750, 1000, 1500, 2000, 2500, 3000, 5000, 7500, 10000]

function applyPreset(p: 'standard' | 'apa' | 'single') {
  if (p === 'standard') { font.value = 'Times New Roman'; size.value = '12pt'; spacing.value = 'Double'; margin.value = 'Normal (1")' }
  if (p === 'apa') { font.value = 'Times New Roman'; size.value = '12pt'; spacing.value = 'Double'; margin.value = 'Normal (1")' }
  if (p === 'single') { font.value = 'Arial'; size.value = '12pt'; spacing.value = 'Single'; margin.value = 'Normal (1")' }
}

const fonts: Font[] = ['Times New Roman', 'Arial', 'Calibri', 'Courier New', 'Georgia']
const sizes: Size[] = ['10pt', '11pt', '12pt', '14pt']
const spacings: Spacing[] = ['Single', '1.5x', 'Double']
const margins: Margin[] = ['Normal (1")', 'Narrow (0.5")', 'Wide (1.5")']
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Words to Pages Converter</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Words to Pages Converter</h1>
      <p class="text-slate-500 text-sm">See exactly how many pages your word count fills at any font, size, and spacing.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Mode toggle -->
      <div class="flex gap-2 p-1 bg-white border border-slate-200 rounded-2xl shadow-sm w-fit">
        <button
          type="button"
          @click="mode = 'words-to-pages'"
          :class="['px-5 py-2 rounded-xl text-sm font-bold transition-all', mode === 'words-to-pages' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-brand-600']"
        >Words → Pages</button>
        <button
          type="button"
          @click="mode = 'pages-to-words'"
          :class="['px-5 py-2 rounded-xl text-sm font-bold transition-all', mode === 'pages-to-words' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-brand-600']"
        >Pages → Words</button>
      </div>

      <!-- Settings -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Formatting Settings</h2>

        <!-- Presets -->
        <div class="flex flex-wrap gap-2 mb-5">
          <span class="text-xs font-semibold text-slate-500 self-center">Quick presets:</span>
          <button type="button" @click="applyPreset('standard')" class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors">Standard essay (12pt TNR, Double)</button>
          <button type="button" @click="applyPreset('apa')" class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors">APA paper (12pt TNR, Double, 1")</button>
          <button type="button" @click="applyPreset('single')" class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors">Single-spaced report (12pt Arial, Single)</button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Font</label>
            <select v-model="font" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none">
              <option v-for="f in fonts" :key="f">{{ f }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Font Size</label>
            <select v-model="size" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none">
              <option v-for="s in sizes" :key="s">{{ s }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Spacing</label>
            <select v-model="spacing" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none">
              <option v-for="sp in spacings" :key="sp">{{ sp }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1.5">Margins</label>
            <select v-model="margin" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none">
              <option v-for="m in margins" :key="m">{{ m }}</option>
            </select>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-3">≈ {{ wordsPerPage.toLocaleString() }} words per page at these settings</p>
      </div>

      <!-- Converter input -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <div v-if="mode === 'words-to-pages'" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Word Count</label>
            <input
              v-model.number="wordInput"
              type="number"
              min="0"
              max="100000"
              class="w-full sm:w-64 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
          <div class="bg-brand-50 border border-brand-100 rounded-2xl p-6 text-center">
            <p class="text-5xl font-extrabold text-brand-600 mb-1">≈ {{ pagesResult }}</p>
            <p class="text-sm font-semibold text-brand-800">pages</p>
            <p class="text-xs text-slate-500 mt-2">This is approximately {{ singleSpacedPages }} single-spaced {{ singleSpacedPages === 1 ? 'page' : 'pages' }}.</p>
          </div>
        </div>
        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Number of Pages</label>
            <input
              v-model.number="pageInput"
              type="number"
              min="0"
              max="10000"
              class="w-full sm:w-64 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
          <div class="bg-brand-50 border border-brand-100 rounded-2xl p-6 text-center">
            <p class="text-5xl font-extrabold text-brand-600 mb-1">≈ {{ wordsResult.toLocaleString() }}</p>
            <p class="text-sm font-semibold text-brand-800">words</p>
          </div>
        </div>
      </div>

      <!-- Reference table -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-700 mb-4">Reference Table — Pages at Current Settings</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="text-left py-2 pr-6 text-xs font-semibold text-slate-500 uppercase tracking-wide">Word Count</th>
                <th class="text-left py-2 pr-6 text-xs font-semibold text-slate-500 uppercase tracking-wide">Pages</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="w in referenceWords" :key="w" class="border-b border-slate-50 hover:bg-slate-50">
                <td class="py-2 pr-6 font-medium text-slate-700">{{ w.toLocaleString() }} words</td>
                <td class="py-2 pr-6 text-slate-600">≈ {{ (Math.round((w / wordsPerPage) * 10) / 10) }} {{ (Math.round((w / wordsPerPage) * 10) / 10) === 1 ? 'page' : 'pages' }}</td>
              </tr>
            </tbody>
          </table>
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
